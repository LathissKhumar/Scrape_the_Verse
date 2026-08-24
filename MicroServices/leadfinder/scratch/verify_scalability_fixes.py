import asyncio
import gc
import os
import sys
import time
import tracemalloc
from unittest.mock import AsyncMock, MagicMock

sys.path.insert(0, os.path.abspath("."))

from leadfinder.agents.scraper import ScraperAgent
from leadfinder.crawler.config import CrawlerConfig
from leadfinder.crawler.result_models import BlockType, CrawlResult


async def benchmark_bounded_concurrency(url_count: int, concurrency_limit: int):
    print(
        f"\n--- Testing Bounded Concurrency: {url_count:,} URLs (Limit: {concurrency_limit}) ---"
    )
    mock_executor = MagicMock()
    mock_executor.config = CrawlerConfig(max_concurrency=concurrency_limit)

    active_now = 0
    max_active = 0
    lock = asyncio.Lock()

    async def mock_crawl(url: str):
        nonlocal active_now, max_active
        async with lock:
            active_now += 1
            max_active = max(max_active, active_now)

        # Simulate small latency
        await asyncio.sleep(0.001)

        async with lock:
            active_now -= 1

        return CrawlResult(
            url=url,
            html="<html><body>Mock Product</body></html>",
            status_code=200,
            blocked=False,
            block_type=BlockType.NONE,
        )

    mock_executor.crawl = AsyncMock(side_effect=mock_crawl)
    scraper = ScraperAgent(browser_executor=mock_executor)

    urls = [f"https://example.com/item/{i}" for i in range(url_count)]

    gc.collect()
    tracemalloc.start()
    t0 = time.time()

    results = await scraper._execute_browser_scrape(
        urls, max_concurrency=concurrency_limit
    )

    duration = time.time() - t0
    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    rps = url_count / duration
    print(f"  Processed {len(results):,} URLs in {duration:.3f}s -> {rps:.1f} RPS")
    print(
        f"  Max Concurrent Coroutines Observed: {max_active} (Configured Limit: {concurrency_limit})"
    )
    print(f"  Peak Memory: {peak_mem / (1024 * 1024):.2f} MB")
    assert max_active <= concurrency_limit
    assert len(results) == url_count


async def main():
    print("=== SCALABILITY & BOUNDED CONCURRENCY BENCHMARK ===")
    for count in [100, 1000, 10000]:
        await benchmark_bounded_concurrency(count, concurrency_limit=10)


if __name__ == "__main__":
    asyncio.run(main())
