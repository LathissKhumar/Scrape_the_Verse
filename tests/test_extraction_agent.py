import pytest
from unittest.mock import AsyncMock

from app.agents.extraction import ExtractionAgent
from app.extraction.engine import ExtractionEngine
from app.extraction.schema import ExtractionResult
from app.models.schemas import ScrapingTask


@pytest.mark.asyncio
async def test_extraction_agent_execution():
    mock_engine = AsyncMock(spec=ExtractionEngine)
    mock_engine.extract_async.return_value = ExtractionResult(
        records=[{"name": "Extracted Item", "price": "$12"}],
        strategy_used="css",
        fallback_used=False,
        metadata={"record_count": 1},
    )

    agent = ExtractionAgent(engine=mock_engine)
    task = ScrapingTask(
        task_id="t_agent",
        objective="Extract items",
        target_urls=["https://example.com"],
        fields=["name", "price"],
    )

    result = await agent.extract(raw_results="<html>...</html>", task=task)
    assert result.strategy_used == "css"
    assert len(result.records) == 1
    assert result.records[0]["name"] == "Extracted Item"
