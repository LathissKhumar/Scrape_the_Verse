import json
import pytest

from leadfinder.agents.planner import ScrapingPlannerAgent, extract_urls_from_text
from leadfinder.llm.exceptions import LLMInvocationError
from leadfinder.models.schemas import ScrapingRequest
from leadfinder.tests.conftest import MockLLMClient


def test_extract_urls_from_text():
    text = "Please scrape https://example.com/items, and also http://store.org/p/123."
    urls = extract_urls_from_text(text)
    assert "https://example.com/items" in urls
    assert "http://store.org/p/123" in urls


def test_extract_urls_from_text_none():
    text = "Extract products and prices from the catalog"
    urls = extract_urls_from_text(text)
    assert urls == []


@pytest.mark.asyncio
async def test_planner_agent_plan_async_success():
    llm_payload = {
        "objective": "Scrape all product listings with price and rating",
        "target_urls": ["https://example.com/products"],
        "fields": ["product_name", "price", "rating"],
        "output_schema": {
            "product_name": "string",
            "price": "string",
            "rating": "number"
        },
        "max_records": 100,
        "constraints": ["Include in-stock only"],
        "source_requirements": []
    }
    mock_llm = MockLLMClient(response_text=json.dumps(llm_payload))
    planner = ScrapingPlannerAgent(llm_client=mock_llm)

    request = ScrapingRequest(
        query="Scrape products from https://example.com/products and get price and rating",
        target_urls=["https://example.com/products"],
        max_records=100,
    )

    task = await planner.plan_async(request=request, task_id="test-task-uuid")

    assert task.task_id == "test-task-uuid"
    assert task.objective == "Scrape all product listings with price and rating"
    assert task.target_urls == ["https://example.com/products"]
    assert task.fields == ["product_name", "price", "rating"]
    assert task.output_schema == {
        "product_name": "string",
        "price": "string",
        "rating": "number"
    }
    assert task.max_records == 100
    assert task.constraints == ["Include in-stock only"]


def test_planner_agent_plan_sync_success():
    llm_payload = {
        "objective": "Scrape book titles",
        "target_urls": ["https://books.example.com"],
        "fields": ["title", "author"],
        "output_schema": {"title": "string", "author": "string"},
        "max_records": 20,
        "constraints": [],
        "source_requirements": []
    }
    mock_llm = MockLLMClient(response_text=json.dumps(llm_payload))
    planner = ScrapingPlannerAgent(llm_client=mock_llm)

    request = ScrapingRequest(
        query="Extract book titles from https://books.example.com",
        target_urls=["https://books.example.com"],
    )

    task = planner.plan(request=request, task_id="sync-task-uuid")
    assert task.task_id == "sync-task-uuid"
    assert task.target_urls == ["https://books.example.com"]
    assert task.fields == ["title", "author"]


@pytest.mark.asyncio
async def test_planner_extracts_urls_from_query_when_target_urls_empty():
    llm_payload = {
        "objective": "Scrape news headlines",
        "target_urls": ["https://news.example.com/world"],
        "fields": ["headline", "timestamp"],
        "output_schema": {"headline": "string", "timestamp": "string"},
        "max_records": None,
        "constraints": [],
        "source_requirements": []
    }
    mock_llm = MockLLMClient(response_text=json.dumps(llm_payload))
    planner = ScrapingPlannerAgent(llm_client=mock_llm)

    request = ScrapingRequest(
        query="Scrape headlines from https://news.example.com/world"
    )

    task = await planner.plan_async(request=request)
    assert "https://news.example.com/world" in task.target_urls
    assert bool(task.task_id)


@pytest.mark.asyncio
async def test_planner_never_invents_urls():
    # If the LLM invents a URL that was not in target_urls nor in the user query, it is discarded
    llm_payload = {
        "objective": "Scrape data",
        "target_urls": ["https://invented-fake-domain.org/data"],
        "fields": ["name"],
        "output_schema": {"name": "string"},
        "max_records": None,
        "constraints": [],
        "source_requirements": []
    }
    mock_llm = MockLLMClient(response_text=json.dumps(llm_payload))
    planner = ScrapingPlannerAgent(llm_client=mock_llm)

    request = ScrapingRequest(
        query="Scrape names from user input",
        target_urls=[],
    )

    task = await planner.plan_async(request=request)
    # The invented URL must NOT be added
    assert task.target_urls == []


@pytest.mark.asyncio
async def test_planner_handles_malformed_json():
    mock_llm = MockLLMClient(response_text="This is not valid JSON at all")
    planner = ScrapingPlannerAgent(llm_client=mock_llm)

    request = ScrapingRequest(query="Scrape items")

    with pytest.raises(LLMInvocationError):
        await planner.plan_async(request=request)
