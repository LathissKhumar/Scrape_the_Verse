"""Circuit breaker to avoid hammering domains that repeatedly return blocks or challenges."""

import time
from typing import Dict
from urllib.parse import urlparse
from leadfinder.crawler.result_models import BlockType


class DomainCircuitBreaker:
    """Tracks consecutive access blocks per domain and trips the circuit to prevent abusive crawls."""

    def __init__(self, failure_threshold: int = 3, cooldown_seconds: float = 60.0):
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds

        self._consecutive_failures: Dict[str, int] = {}
        self._circuit_open_until: Dict[str, float] = {}

    def _get_domain(self, url: str) -> str:
        return urlparse(url).netloc.lower() or "default"

    def allow_request(self, url: str) -> bool:
        """Check if request to domain is allowed or if circuit is currently open."""
        domain = self._get_domain(url)
        open_until = self._circuit_open_until.get(domain, 0.0)
        if time.time() < open_until:
            return False
        return True

    def record_result(self, url: str, blocked: bool, block_type: BlockType) -> None:
        """Record outcome of a crawl attempt."""
        domain = self._get_domain(url)

        if blocked and block_type in (
            BlockType.ACCESS_DENIED,
            BlockType.CAPTCHA,
            BlockType.SECURITY_CHALLENGE,
            BlockType.RATE_LIMITED,
        ):
            count = self._consecutive_failures.get(domain, 0) + 1
            self._consecutive_failures[domain] = count
            if count >= self.failure_threshold:
                self._circuit_open_until[domain] = time.time() + self.cooldown_seconds
        else:
            # Successful crawl resets consecutive failure counter
            self._consecutive_failures[domain] = 0

    def get_failure_count(self, url: str) -> int:
        domain = self._get_domain(url)
        return self._consecutive_failures.get(domain, 0)
