import pytest
from app.crawler.browser_manager import BrowserManager
from app.crawler.browser_executor import BrowserExecutor
from app.crawler.config import CrawlerConfig
from app.crawler.action_models import ActionPlan, WaitForAction, ScrollAction, ExtractAction
from app.crawler.result_models import BlockType


@pytest.mark.asyncio
async def test_browser_executor_lifecycle_and_crawl():
    config = CrawlerConfig(headless=True, timeout_ms=30000)
    manager = BrowserManager(config=config)
    executor = BrowserExecutor(browser_manager=manager)

    try:
        url = "https://example.com"
        plan = ActionPlan(
            url=url,
            actions=[
                WaitForAction(selector="h1", timeout_ms=5000),
                ExtractAction(fields={"heading": "h1"}),
            ],
        )
        res = await executor.crawl(url=url, action_plan=plan)

        assert res.success is True
        assert res.status_code == 200
        assert "Example Domain" in res.html
        assert res.blocked is False
        assert res.block_type == BlockType.NONE
        assert res.extracted_data == {"heading": "Example Domain"}
    finally:
        await manager.close()


@pytest.mark.asyncio
async def test_browser_executor_ssrf_blocking():
    config = CrawlerConfig(headless=True)
    manager = BrowserManager(config=config)
    executor = BrowserExecutor(browser_manager=manager)

    try:
        # Loopback URL
        res = await executor.crawl("http://127.0.0.1:8000/test")
        assert res.blocked is True
        assert res.block_type == BlockType.ACCESS_DENIED
        assert "SSRF" in (res.error or "")
    finally:
        await manager.close()
