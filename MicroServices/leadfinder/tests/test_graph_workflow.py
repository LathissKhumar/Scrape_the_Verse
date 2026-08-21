import pytest
from unittest.mock import AsyncMock

from leadfinder.agents.extraction import ExtractionAgent
from leadfinder.agents.planner import ScrapingPlannerAgent
from leadfinder.agents.scraper import ScraperAgent
from leadfinder.agents.validation import ValidationAgent
from leadfinder.extraction.schema import ExtractionResult
from leadfinder.graph.state import ScrapingGraphState
from leadfinder.graph.workflow import create_scraping_workflow
from leadfinder.models.schemas import ScrapingTask
from leadfinder.validation.schemas import ValidationResult


@pytest.mark.asyncio
async def test_workflow_execution_success():
    mock_planner = AsyncMock(spec=ScrapingPlannerAgent)
    mock_planner.plan_async.return_value = ScrapingTask(
        task_id="wf_task_1",
        objective="Scrape books",
        target_urls=["https://books.example.com"],
        fields=["title", "price"],
    )

    mock_scraper = AsyncMock(spec=ScraperAgent)
    mock_scraper.execute.return_value = [
        {"title": "Book 1", "price": "$15"},
        {"title": "Book 2", "price": "$20"},
    ]

    mock_extractor = AsyncMock(spec=ExtractionAgent)
    mock_extractor.extract.return_value = ExtractionResult(
        records=[
            {"title": "Book 1", "price": "$15"},
            {"title": "Book 2", "price": "$20"},
        ],
        strategy_used="passthrough",
        fallback_used=False,
    )

    mock_validator = AsyncMock(spec=ValidationAgent)
    mock_validator.validate.return_value = ValidationResult(
        status="healthy",
        health_score=0.95,
        quality_score=0.92,
        record_count=2,
    )

    workflow = create_scraping_workflow(
        planner_agent=mock_planner,
        scraper_agent=mock_scraper,
        extraction_agent=mock_extractor,
        validation_agent=mock_validator,
    )

    initial_state: ScrapingGraphState = {
        "task_id": "wf_task_1",
        "original_user_query": "Scrape books from https://books.example.com",
        "target_urls": ["https://books.example.com"],
    }

    final_state = await workflow.ainvoke(initial_state)

    assert final_state["scraping_task"] is not None
    assert final_state["scraping_task"].task_id == "wf_task_1"
    assert final_state["raw_results"] == [
        {"title": "Book 1", "price": "$15"},
        {"title": "Book 2", "price": "$20"},
    ]
    assert final_state["extracted_results"] == [
        {"title": "Book 1", "price": "$15"},
        {"title": "Book 2", "price": "$20"},
    ]
    assert final_state["final_output"] is not None
    assert final_state["final_output"].status == "success"
    assert len(final_state["final_output"].records) == 2


@pytest.mark.asyncio
async def test_workflow_execution_empty_results():
    mock_planner = AsyncMock(spec=ScrapingPlannerAgent)
    mock_planner.plan_async.return_value = ScrapingTask(
        task_id="wf_task_2",
        objective="Scrape catalog",
        target_urls=["https://example.com/empty"],
        fields=["item"],
    )

    mock_scraper = AsyncMock(spec=ScraperAgent)
    mock_scraper.execute.return_value = []

    workflow = create_scraping_workflow(
        planner_agent=mock_planner,
        scraper_agent=mock_scraper,
    )

    initial_state: ScrapingGraphState = {
        "task_id": "wf_task_2",
        "original_user_query": "Scrape catalog from https://example.com/empty",
        "target_urls": ["https://example.com/empty"],
    }

    final_state = await workflow.ainvoke(initial_state)

    assert final_state["final_output"] is not None
    assert final_state["final_output"].status == "failed"


@pytest.mark.asyncio
async def test_workflow_execution_scraper_failure():
    mock_planner = AsyncMock(spec=ScrapingPlannerAgent)
    mock_planner.plan_async.return_value = ScrapingTask(
        task_id="wf_task_3",
        objective="Scrape failure test",
        target_urls=["https://example.com/blocked"],
        fields=["item"],
    )

    mock_scraper = AsyncMock(spec=ScraperAgent)
    mock_scraper.execute.side_effect = RuntimeError("Bright Data connection failed")

    workflow = create_scraping_workflow(
        planner_agent=mock_planner,
        scraper_agent=mock_scraper,
    )

    initial_state: ScrapingGraphState = {
        "task_id": "wf_task_3",
        "original_user_query": "Scrape failure test",
        "target_urls": ["https://example.com/blocked"],
    }

    final_state = await workflow.ainvoke(initial_state)

    assert final_state["final_output"] is not None
    assert final_state["final_output"].status == "failed"
    assert final_state["failure"]["failure_type"] == "SCRAPER_EXECUTION_FAILURE"
