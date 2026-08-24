"""Per-domain rate limiter with token bucket, jittered backoff, and HTTP 429 Retry-After support."""

import asyncio
import random
import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from urllib.parse import urlparse


class DomainRateLimiter:
    """Controls request rates and concurrency per domain with jittered exponential backoff on 429s."""

    def __init__(
        self,
        requests_per_second: float = 2.0,
        max_concurrency: int = 3,
        default_backoff_seconds: float = 5.0,
    ):
        self.requests_per_second = requests_per_second
        self.min_interval = (
            1.0 / requests_per_second if requests_per_second > 0 else 0.5
        )
        self.max_concurrency = max_concurrency
        self.default_backoff_seconds = default_backoff_seconds

        self._last_request_time: dict[str, float] = {}
        self._blocked_until: dict[str, float] = {}
        self._semaphores: dict[str, asyncio.Semaphore] = {}
        self._lock = asyncio.Lock()

    def _get_domain(self, url: str) -> str:
        return urlparse(url).netloc.lower() or "default"

    def record_429(self, url: str, retry_after_seconds: float | None = None) -> None:
        """Record HTTP 429 rate limit response and pause domain crawling with randomized jitter."""
        domain = self._get_domain(url)
        base_pause = (
            retry_after_seconds
            if (retry_after_seconds and retry_after_seconds > 0)
            else self.default_backoff_seconds
        )
        # Add 10-25% randomized jitter to prevent synchronized thundering herd
        jitter = random.uniform(0.1, 0.25) * base_pause
        self._blocked_until[domain] = time.time() + base_pause + jitter

    def is_rate_limited(self, url: str) -> bool:
        """Check if domain is currently in a 429 cooldown window."""
        domain = self._get_domain(url)
        blocked_until = self._blocked_until.get(domain, 0.0)
        return time.time() < blocked_until

    async def acquire(self, url: str) -> None:
        """Acquire rate-limited token and enforce per-domain spacing."""
        domain = self._get_domain(url)

        # Check 429 cooldown
        blocked_until = self._blocked_until.get(domain, 0.0)
        now = time.time()
        if now < blocked_until:
            wait_time = blocked_until - now
            await asyncio.sleep(wait_time)

        # Enforce rate spacing
        async with self._lock:
            last_time = self._last_request_time.get(domain, 0.0)
            now = time.time()
            elapsed = now - last_time
            if elapsed < self.min_interval:
                delay = self.min_interval - elapsed
                await asyncio.sleep(delay)
            self._last_request_time[domain] = time.time()

    @asynccontextmanager
    async def slot(self, url: str) -> AsyncGenerator[None, None]:
        """Context manager enforcing both per-domain concurrency limits and spacing."""
        domain = self._get_domain(url)
        async with self._lock:
            if domain not in self._semaphores:
                self._semaphores[domain] = asyncio.Semaphore(self.max_concurrency)
            sem = self._semaphores[domain]

        async with sem:
            await self.acquire(url)
            yield
