import pytest
from leadfinder.agents.validation import ValidationAgent
from leadfinder.models.schemas import ScrapingTask


@pytest.mark.asyncio
async def test_validation_agent_async_run():
    agent = ValidationAgent()
    task = ScrapingTask(
        task_id="t_agent_val",
        objective="Scrape items",
        target_urls=["https://example.com"],
        fields=["name", "price"],
    )
    records = [{"name": "Item 1", "price": "$10"}]

    result = await agent.validate(extracted_results=records, task=task)
    assert result.status == "healthy"
    assert result.health_score > 0.8
    assert result.record_count == 1
