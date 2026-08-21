import pytest
from unittest.mock import AsyncMock, MagicMock
from leadfinder.agents.diagnosis import DiagnosisAgent
from leadfinder.agents.healing import HealingAgent
from leadfinder.agents.planner import ScrapingPlannerAgent
from leadfinder.agents.scraper import ScraperAgent
from leadfinder.agents.validation import ValidationAgent
from leadfinder.diagnosis.schemas import DiagnosisResult, RootCause
from leadfinder.extraction.schema import ExtractionSchema, ExtractionStrategyEnum, FieldRule
from leadfinder.graph.state import ScrapingGraphState
from leadfinder.graph.workflow import create_scraping_workflow
from leadfinder.healing.schemas import PerformanceSnapshot, RepairEvaluation, RepairPlan, RepairType
from leadfinder.models.schemas import ScrapingRequest, ScrapingResult, ScrapingTask
from leadfinder.validation.schemas import FieldMetric, ValidationResult


@pytest.mark.asyncio
async def test_workflow_healthy_bypasses_healing():
    mock_planner = MagicMock()
    mock_planner.plan_async = AsyncMock(
        return_value=ScrapingTask(task_id="t1", objective="Scrape", target_urls=["https://example.com"])
    )

    mock_scraper = MagicMock()
    mock_scraper.execute = AsyncMock(return_value=[{"html": "<div>Clean</div>"}])

    mock_validator = MagicMock()
    mock_validator.validate = AsyncMock(
        return_value=ValidationResult(health_score=0.95, quality_score=0.95, status="healthy", record_count=1)
    )

    workflow = create_scraping_workflow(
        planner_agent=mock_planner,
        scraper_agent=mock_scraper,
        validation_agent=mock_validator,
    )

    initial_state: ScrapingGraphState = {
        "task_id": "t1",
        "original_user_query": "Scrape site",
        "target_urls": ["https://example.com"],
    }

    final_state = await workflow.ainvoke(initial_state)
    result = final_state.get("final_output")

    assert result.status == "success"
    assert result.metadata.get("health_score") == 0.95
    assert final_state.get("diagnosis_result") is None


@pytest.mark.asyncio
async def test_workflow_source_data_quality_bypasses_repair():
    mock_planner = MagicMock()
    mock_planner.plan_async = AsyncMock(
        return_value=ScrapingTask(task_id="t1", objective="Scrape", target_urls=["https://example.com"])
    )

    mock_scraper = MagicMock()
    mock_scraper.execute = AsyncMock(return_value=[{"html": "<div>No data on source</div>"}])

    mock_validator = MagicMock()
    # Degraded validation
    mock_validator.validate = AsyncMock(
        return_value=ValidationResult(health_score=0.40, status="degraded", record_count=0)
    )

    mock_diagnosis = MagicMock()
    mock_diagnosis.diagnose = AsyncMock(
        return_value=DiagnosisResult(
            root_cause=RootCause.SOURCE_DATA_QUALITY,
            confidence=0.9,
            evidence=["Target page is empty by design"],
        )
    )

    mock_healing = MagicMock()

    workflow = create_scraping_workflow(
        planner_agent=mock_planner,
        scraper_agent=mock_scraper,
        validation_agent=mock_validator,
        diagnosis_agent=mock_diagnosis,
        healing_agent=mock_healing,
    )

    initial_state: ScrapingGraphState = {
        "task_id": "t1",
        "original_user_query": "Scrape site",
        "target_urls": ["https://example.com"],
    }

    final_state = await workflow.ainvoke(initial_state)
    mock_healing.heal.assert_not_called()


@pytest.mark.asyncio
async def test_workflow_heals_broken_scrape_successfully():
    mock_planner = MagicMock()
    mock_planner.plan_async = AsyncMock(
        return_value=ScrapingTask(task_id="t1", objective="Scrape products", target_urls=["https://example.com"])
    )

    mock_scraper = MagicMock()
    mock_scraper.execute = AsyncMock(return_value=[{"html": "<div class='product-item'><h2 class='name'>Phone</h2></div>"}])

    mock_validator = MagicMock()
    # Initial validation is broken
    mock_validator.validate = AsyncMock(
        return_value=ValidationResult(health_score=0.30, quality_score=0.35, status="broken", record_count=0)
    )

    mock_diagnosis = MagicMock()
    mock_diagnosis.diagnose = AsyncMock(
        return_value=DiagnosisResult(root_cause=RootCause.SELECTOR_DRIFT, confidence=0.90, affected_fields=["name"])
    )

    mock_healing = MagicMock()
    evaluation = RepairEvaluation(
        repair_id="rep-1",
        before=PerformanceSnapshot(health=0.30, quality=0.35, records=0),
        after=PerformanceSnapshot(health=0.95, quality=0.92, records=10),
        improvement=0.65,
        critical_failure_resolved=True,
        regression_detected=False,
        accepted=True,
    )
    mock_healing.heal = AsyncMock(
        return_value=(
            True,
            ExtractionSchema(strategy=ExtractionStrategyEnum.CSS, fields=[FieldRule(name="name", selector=".name")]),
            evaluation,
            [{"name": "Phone"}],
            [{"attempt": 1, "repair_type": "REPAIR_CSS_SELECTORS", "health_before": 0.30, "health_after": 0.95, "accepted": True}],
        )
    )

    workflow = create_scraping_workflow(
        planner_agent=mock_planner,
        scraper_agent=mock_scraper,
        validation_agent=mock_validator,
        diagnosis_agent=mock_diagnosis,
        healing_agent=mock_healing,
    )

    initial_state: ScrapingGraphState = {
        "task_id": "t1",
        "original_user_query": "Scrape phone",
        "target_urls": ["https://example.com"],
    }

    final_state = await workflow.ainvoke(initial_state)
    result = final_state.get("final_output")

    assert result.status == "success"
    assert result.metadata["self_healed"] is True
    assert result.metadata["repair_type"] == "REPAIR_CSS_SELECTORS"
    assert result.metadata["health_after"] == 0.95
    assert len(result.records) == 1
