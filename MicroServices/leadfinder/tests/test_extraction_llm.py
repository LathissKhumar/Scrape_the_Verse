import json

import pytest

from leadfinder.extraction.llm import LLMExtractor
from leadfinder.models.schemas import ScrapingTask
from leadfinder.tests.conftest import MockLLMClient


@pytest.mark.asyncio
async def test_llm_extractor_async_success():
    mock_response = json.dumps(
        [
            {"product_name": "Gadget Pro", "price": "$199.99", "rating": 4.8},
            {"product_name": "Gadget Mini", "price": "$99.99", "rating": 4.2},
        ]
    )
    mock_llm = MockLLMClient(response_text=mock_response)
    extractor = LLMExtractor(llm_client=mock_llm)

    task = ScrapingTask(
        task_id="t_llm",
        objective="Extract gadgets",
        target_urls=["https://example.com/gadgets"],
        fields=["product_name", "price", "rating"],
    )

    records = await extractor.extract_async("Page text about gadgets", task)
    assert len(records) == 2
    assert records[0]["product_name"] == "Gadget Pro"
    assert records[0]["price"] == "$199.99"


def test_llm_extractor_sync_success():
    mock_response = json.dumps(
        [
            {"company": "Acme Corp", "employees": 500},
        ]
    )
    mock_llm = MockLLMClient(response_text=mock_response)
    extractor = LLMExtractor(llm_client=mock_llm)

    task = ScrapingTask(
        task_id="t_llm_sync",
        objective="Extract companies",
        target_urls=["https://example.com/companies"],
        fields=["company", "employees"],
    )

    records = extractor.extract("Company directory info", task)
    assert len(records) == 1
    assert records[0]["company"] == "Acme Corp"
