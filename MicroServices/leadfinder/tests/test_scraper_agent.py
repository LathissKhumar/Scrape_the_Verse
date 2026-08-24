from unittest.mock import AsyncMock

import pytest

from leadfinder.agents.scraper import ScraperAgent
from leadfinder.brightdata.client import BrightDataClient
from leadfinder.brightdata.exceptions import BrightDataJobError
from leadfinder.models.schemas import ScrapingTask


@pytest.mark.asyncio
async def test_scraper_agent_empty_urls_raises():
    agent = ScraperAgent()
    task = ScrapingTask(
        task_id="t_empty",
        objective="Scrape without URL",
        target_urls=[],
        fields=["name"],
    )
    with pytest.raises(ValueError) as exc:
        await agent.execute(task=task)
    assert "No target URL was supplied" in str(exc.value)


@pytest.mark.asyncio
async def test_scraper_agent_success():
    mock_client = AsyncMock(spec=BrightDataClient)
    mock_client.is_configured = True
    mock_client.scrape_and_collect.return_value = [
        {"product": "Laptop", "price": "$999"},
        {"product": "Mouse", "price": "$29"},
    ]

    agent = ScraperAgent(brightdata_client=mock_client)
    task = ScrapingTask(
        task_id="t_success",
        objective="Scrape tech items",
        target_urls=["https://store.example.com/tech"],
        fields=["product", "price"],
    )

    records = await agent.execute(task=task)
    assert len(records) == 2
    assert records[0]["product"] == "Laptop"


@pytest.mark.asyncio
async def test_scraper_agent_client_error_propagates():
    mock_client = AsyncMock(spec=BrightDataClient)
    mock_client.is_configured = True
    mock_client.scrape_and_collect.side_effect = BrightDataJobError(
        "Collector failed on remote server"
    )

    agent = ScraperAgent(brightdata_client=mock_client)
    task = ScrapingTask(
        task_id="t_err",
        objective="Scrape",
        target_urls=["https://example.com"],
        fields=["name"],
    )

    with pytest.raises(BrightDataJobError) as exc:
        await agent.execute(task=task)
    assert "Collector failed" in str(exc.value)
