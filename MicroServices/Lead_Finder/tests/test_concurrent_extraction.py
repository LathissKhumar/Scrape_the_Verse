from unittest.mock import AsyncMock, MagicMock

import pytest
from leadfinder.extraction.llm import LLMExtractor
from leadfinder.models.schemas import ScrapingTask


@pytest.mark.asyncio
async def test_llm_extractor_concurrent_chunks():
    mock_llm = MagicMock()
    mock_llm.invoke = AsyncMock(
        side_effect=[
            '[{"title": "Item 1", "price": "$10"}]',
            '[{"title": "Item 2", "price": "$20"}]',
        ]
    )
    extractor = LLMExtractor(llm_client=mock_llm)
    task = ScrapingTask(
        task_id="t1",
        objective="Scrape items",
        target_urls=["https://example.com"],
        fields=["title", "price"],
    )

    long_content = "Item 1 description\n\n" * 100 + "\n\nItem 2 description\n\n" * 100
    records = await extractor.extract_async(
        content=long_content,
        task=task,
    )
    assert len(records) >= 1
    assert any(
        "Item 1" in str(r.values()) or "Item 2" in str(r.values()) for r in records
    )
