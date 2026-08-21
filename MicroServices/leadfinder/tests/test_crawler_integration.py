import pytest
from leadfinder.agents.scraper import ScraperAgent
from leadfinder.crawler.browser_executor import BrowserExecutor
from leadfinder.crawler.config import CrawlerConfig
from leadfinder.models.schemas import ScrapingTask


@pytest.mark.asyncio
async def test_scraper_agent_with_browser_executor():
    config = CrawlerConfig(headless=True, timeout_ms=30000)
    executor = BrowserExecutor()
    scraper = ScraperAgent(brightdata_client=None, browser_executor=executor)

    task = ScrapingTask(
        task_id="test_crawler_integ",
        objective="Scrape title from example.com",
        target_urls=["https://example.com"],
        fields=["title"],
        metadata={"scraper_provider": "browser"},
    )

    try:
        results = await scraper.execute(task=task)
        assert len(results) == 1
        record = results[0]
        assert record["url"] == "https://example.com"
        assert record["status_code"] == 200
        assert "Example Domain" in record["html"]
        assert record["blocked"] is False
        assert record["block_type"] == "NONE"
    finally:
        await executor.browser_manager.close()
