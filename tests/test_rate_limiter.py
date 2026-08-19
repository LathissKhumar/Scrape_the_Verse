import asyncio
import pytest
from app.crawler.rate_limiter import DomainRateLimiter


@pytest.mark.asyncio
async def test_domain_rate_limiter_throttling():
    limiter = DomainRateLimiter(requests_per_second=10.0, max_concurrency=2)
    
    # Acquire token for domain
    t0 = asyncio.get_event_loop().time()
    await limiter.acquire("https://example.com/page1")
    await limiter.acquire("https://example.com/page2")
    t1 = asyncio.get_event_loop().time()
    
    assert (t1 - t0) >= 0.05  # Throttled by requests_per_second


@pytest.mark.asyncio
async def test_domain_rate_limiter_retry_after():
    limiter = DomainRateLimiter()
    limiter.record_429("https://example.com/item", retry_after_seconds=0.2)
    
    assert limiter.is_rate_limited("https://example.com/item") is True
    await asyncio.sleep(0.25)
    assert limiter.is_rate_limited("https://example.com/item") is False
