from unittest.mock import AsyncMock, MagicMock

import pytest
from leadfinder.agents.planner import ScrapingPlannerAgent


@pytest.mark.asyncio
async def test_planner_detects_search_and_deep_crawl():
    mock_llm = MagicMock()
    mock_llm.invoke_async = AsyncMock(
        return_value='{"objective": "Search redmi", "fields": ["product_name", "price", "specifications"], "max_records": 10}'
    )
    planner = ScrapingPlannerAgent(llm_client=mock_llm)
    task = await planner.plan_async(
        query="search redmi on flipkart and get specifications for top 10 items",
        target_urls=["https://www.flipkart.com"],
    )
    assert task.is_search is True
    assert "redmi" in (task.search_keyword or "").lower()
    assert task.deep_crawl is True
    assert task.max_detail_pages == 10


@pytest.mark.asyncio
async def test_planner_defaults_to_direct_crawl_for_standard_url():
    mock_llm = MagicMock()
    mock_llm.invoke_async = AsyncMock(
        return_value='{"objective": "Extract item", "fields": ["title", "price"]}'
    )
    planner = ScrapingPlannerAgent(llm_client=mock_llm)
    task = await planner.plan_async(
        query="extract title and price",
        target_urls=["https://example.com/item/1"],
    )
    assert task.is_search is False
    assert task.deep_crawl is False
