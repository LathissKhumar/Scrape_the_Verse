import pytest
from unittest.mock import AsyncMock

from leadfinder.agents.diagnosis import DiagnosisAgent
from leadfinder.agents.extraction import ExtractionAgent
from leadfinder.agents.planner import ScrapingPlannerAgent
from leadfinder.agents.scraper import ScraperAgent
from leadfinder.agents.validation import ValidationAgent
from leadfinder.diagnosis.schemas import DiagnosisResult, RepairStrategy, RootCause
from leadfinder.extraction.schema import ExtractionResult
from leadfinder.graph.state import ScrapingGraphState
from leadfinder.graph.workflow import create_scraping_workflow
from leadfinder.models.schemas import ScrapingTask
from leadfinder.validation.schemas import FailureItem, FailureTaxonomy, ValidationResult


@pytest.mark.asyncio
async def test_workflow_healthy_bypasses_diagnosis():
    mock_planner = AsyncMock(spec=ScrapingPlannerAgent)
    mock_planner.plan_async.return_value = ScrapingTask(
        task_id="wf_healthy",
        objective="Scrape books",
        target_urls=["https://books.example.com"],
        fields=["title", "price"],
    )

    mock_scraper = AsyncMock(spec=ScraperAgent)
    mock_scraper.execute.return_value = [{"title": "Book 1", "price": "$15"}]

    mock_extractor = AsyncMock(spec=ExtractionAgent)
    mock_extractor.extract.return_value = ExtractionResult(
        records=[{"title": "Book 1", "price": "$15"}],
        strategy_used="passthrough",
    )

    mock_validator = AsyncMock(spec=ValidationAgent)
    mock_validator.validate.return_value = ValidationResult(
        status="healthy",
        health_score=0.98,
        record_count=1,
    )

    mock_diagnostician = AsyncMock(spec=DiagnosisAgent)

    workflow = create_scraping_workflow(
        planner_agent=mock_planner,
        scraper_agent=mock_scraper,
        extraction_agent=mock_extractor,
        validation_agent=mock_validator,
        diagnosis_agent=mock_diagnostician,
    )

    state: ScrapingGraphState = {
        "task_id": "wf_healthy",
        "original_user_query": "Scrape books from https://books.example.com",
        "target_urls": ["https://books.example.com"],
    }

    final_state = await workflow.ainvoke(state)

    assert final_state["validation_result"]["status"] == "healthy"
    assert "diagnosis_result" not in final_state or final_state["diagnosis_result"] is None
    mock_diagnostician.diagnose.assert_not_called()


@pytest.mark.asyncio
async def test_workflow_degraded_routes_to_diagnosis():
    mock_planner = AsyncMock(spec=ScrapingPlannerAgent)
    mock_planner.plan_async.return_value = ScrapingTask(
        task_id="wf_degraded",
        objective="Scrape books",
        target_urls=["https://books.example.com"],
        fields=["title", "price"],
    )

    mock_scraper = AsyncMock(spec=ScraperAgent)
    mock_scraper.execute.return_value = [{"title": "Book 1"}]

    mock_extractor = AsyncMock(spec=ExtractionAgent)
    mock_extractor.extract.return_value = ExtractionResult(
        records=[{"title": "Book 1", "price": None}],
        strategy_used="css",
    )

    mock_validator = AsyncMock(spec=ValidationAgent)
    mock_validator.validate.return_value = ValidationResult(
        status="unstable",
        health_score=0.45,
        record_count=1,
        failures=[
            FailureItem(
                failure_type=FailureTaxonomy.LOW_FIELD_COVERAGE,
                severity="high",
                message="Price field empty",
            )
        ],
    )

    mock_diagnostician = AsyncMock(spec=DiagnosisAgent)
    mock_diagnostician.diagnose.return_value = DiagnosisResult(
        diagnosis_status="diagnosed",
        root_cause=RootCause.SELECTOR_DRIFT,
        confidence=0.92,
        repair_strategy=RepairStrategy.REPAIR_CSS_SELECTORS,
    )

    workflow = create_scraping_workflow(
        planner_agent=mock_planner,
        scraper_agent=mock_scraper,
        extraction_agent=mock_extractor,
        validation_agent=mock_validator,
        diagnosis_agent=mock_diagnostician,
    )

    state: ScrapingGraphState = {
        "task_id": "wf_degraded",
        "original_user_query": "Scrape books from https://books.example.com",
        "target_urls": ["https://books.example.com"],
    }

    final_state = await workflow.ainvoke(state)

    assert final_state["diagnosis_result"] is not None
    assert final_state["diagnosis_result"]["root_cause"] == "SELECTOR_DRIFT"
    assert "diagnosis" in final_state["final_output"].metadata
    mock_diagnostician.diagnose.assert_called_once()
