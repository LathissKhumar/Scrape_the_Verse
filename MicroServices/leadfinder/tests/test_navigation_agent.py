from unittest.mock import AsyncMock, MagicMock
import pytest
from leadfinder.agents.navigation import NavigationAgent
from leadfinder.models.schemas import ScrapingTask


@pytest.mark.asyncio
async def test_navigation_agent_executes_search_and_harvest():
    mock_browser_mgr = MagicMock()
    mock_context = AsyncMock()
    mock_page = AsyncMock()
    mock_page.content = AsyncMock(return_value="""
    <html><body>
      <div class="product"><a href="/phone-1/p/itm1">Phone 1</a></div>
      <div class="product"><a href="/phone-2/p/itm2">Phone 2</a></div>
    </body></html>
    """)
    mock_page.url = "https://www.flipkart.com/search?q=redmi"
    mock_context.new_page = AsyncMock(return_value=mock_page)
    mock_browser_mgr.create_isolated_context = AsyncMock(return_value=mock_context)

    mock_navigator = MagicMock()
    mock_navigator.search = AsyncMock(return_value=True)

    agent = NavigationAgent(
        browser_manager=mock_browser_mgr,
        navigator_engine=mock_navigator,
    )
    task = ScrapingTask(
        task_id="t1",
        objective="Search redmi",
        target_urls=["https://www.flipkart.com"],
        fields=["name", "price"],
        is_search=True,
        search_keyword="redmi",
        deep_crawl=True,
        max_detail_pages=2,
    )
    detail_urls = await agent.run(task)
    assert len(detail_urls) == 2
    assert "https://www.flipkart.com/phone-1/p/itm1" in detail_urls
    assert "https://www.flipkart.com/phone-2/p/itm2" in detail_urls


@pytest.mark.asyncio
async def test_navigation_agent_falls_back_when_no_search_needed():
    agent = NavigationAgent()
    task = ScrapingTask(
        task_id="t2",
        objective="Scrape exact target",
        target_urls=["https://example.com/item/1"],
        fields=["name"],
        is_search=False,
        deep_crawl=False,
    )
    urls = await agent.run(task)
    assert urls == ["https://example.com/item/1"]
