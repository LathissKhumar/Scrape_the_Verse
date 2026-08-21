import pytest
from unittest.mock import AsyncMock, MagicMock
from leadfinder.diagnosis.schemas import DiagnosisResult, RootCause
from leadfinder.extraction.schema import ExtractionResult, ExtractionSchema, ExtractionStrategyEnum, FieldRule, RawPage
from leadfinder.healing.engine import HealingEngine
from leadfinder.healing.schemas import RepairCandidate, RepairPlan, RepairType
from leadfinder.models.schemas import ScrapingTask
from leadfinder.validation.schemas import FieldMetric, ValidationResult


@pytest.mark.asyncio
async def test_healing_engine_successful_canary_acceptance():
    # Setup mocks
    mock_collector = MagicMock()
    mock_collector.check_transient_recovery = AsyncMock(
        return_value=([RawPage(url="https://example.com", html="<div class='product'><h2 class='name'>Phone</h2><span class='price'>$500</span></div>")], False, None)
    )

    mock_planner = MagicMock()
    plan = RepairPlan(
        repair_type=RepairType.REPAIR_CSS_SELECTORS,
        affected_fields=["name"],
        proposed_configuration={"name": ".name"},
        patch={"fields": [{"name": "name", "selector": ".name"}]},
        reason="Update selector",
        confidence=0.9,
    )
    mock_planner.generate_candidates = AsyncMock(return_value=[RepairCandidate(plan=plan, score=0.9, rank=1)])

    mock_extractor = MagicMock()
    mock_extractor.extract = AsyncMock(return_value=ExtractionResult(records=[{"name": "Phone", "price": "$500"}], strategy_used="css"))

    mock_validator = MagicMock()
    mock_validator.validate = AsyncMock(return_value=ValidationResult(
        health_score=0.95,
        quality_score=0.95,
        status="healthy",
        record_count=1,
        field_metrics={"name": FieldMetric(coverage=1.0, valid_count=1), "price": FieldMetric(coverage=1.0, valid_count=1)},
    ))

    engine = HealingEngine(
        evidence_collector=mock_collector,
        planner=mock_planner,
        extraction_engine=mock_extractor,
        validation_engine=mock_validator,
    )

    task = ScrapingTask(task_id="t1", objective="Scrape phone", target_urls=["https://example.com"])
    diagnosis = DiagnosisResult(root_cause=RootCause.SELECTOR_DRIFT, confidence=0.9, affected_fields=["name"])
    initial_validation = ValidationResult(
        health_score=0.30,
        quality_score=0.30,
        status="broken",
        record_count=1,
        field_metrics={"name": FieldMetric(coverage=0.0), "price": FieldMetric(coverage=1.0, valid_count=1)},
    )
    initial_schema = ExtractionSchema(strategy=ExtractionStrategyEnum.CSS, fields=[FieldRule(name="name", selector=".old-name"), FieldRule(name="price", selector=".price")])

    success, healed_schema, evaluation, records, history = await engine.heal(
        task=task,
        diagnosis=diagnosis,
        validation=initial_validation,
        current_schema=initial_schema,
    )

    assert success is True
    assert evaluation.accepted is True
    assert len(records) == 1
    assert healed_schema.fields[0].selector == ".name"
    assert len(history) == 1
    assert history[0]["accepted"] is True


@pytest.mark.asyncio
async def test_healing_engine_escalates_when_candidates_exhausted():
    mock_collector = MagicMock()
    mock_collector.check_transient_recovery = AsyncMock(
        return_value=([RawPage(url="https://example.com", html="<html>Empty</html>")], False, None)
    )

    mock_planner = MagicMock()
    plan = RepairPlan(
        repair_type=RepairType.REPAIR_CSS_SELECTORS,
        reason="Tweak selector",
        confidence=0.5,
    )
    mock_planner.generate_candidates = AsyncMock(return_value=[RepairCandidate(plan=plan, score=0.4, rank=1)])

    mock_extractor = MagicMock()
    mock_extractor.extract = AsyncMock(return_value=ExtractionResult(records=[], strategy_used="css"))

    # Validator still returns broken result
    mock_validator = MagicMock()
    mock_validator.validate = AsyncMock(return_value=ValidationResult(
        health_score=0.20,
        status="broken",
        record_count=0,
    ))

    engine = HealingEngine(
        evidence_collector=mock_collector,
        planner=mock_planner,
        extraction_engine=mock_extractor,
        validation_engine=mock_validator,
        max_repair_attempts=1,
    )

    task = ScrapingTask(task_id="t1", objective="Scrape", target_urls=["https://example.com"])
    diagnosis = DiagnosisResult(root_cause=RootCause.SELECTOR_DRIFT, confidence=0.5)
    initial_validation = ValidationResult(health_score=0.20, status="broken")
    initial_schema = ExtractionSchema(strategy=ExtractionStrategyEnum.CSS)

    success, healed_schema, evaluation, records, history = await engine.heal(
        task=task,
        diagnosis=diagnosis,
        validation=initial_validation,
        current_schema=initial_schema,
    )

    assert success is False
    assert evaluation.accepted is False
    assert len(history) == 1
    assert history[0]["accepted"] is False
