import pytest
from leadfinder.diagnosis.schemas import DiagnosisResult, RootCause
from leadfinder.healing.evaluator import RepairEvaluator
from leadfinder.healing.schemas import RepairPlan, RepairType
from leadfinder.validation.schemas import (
    DuplicateMetric,
    FailureItem,
    FailureTaxonomy,
    FieldMetric,
    SchemaMetric,
    UrlMetric,
    ValidationResult,
)


def _make_val_result(
    health: float,
    quality: float,
    coverage: dict[str, float],
    dup_rate: float = 0.0,
    schema_valid: float = 1.0,
    failures: list[FailureItem] = None,
) -> ValidationResult:
    field_metrics = {
        k: FieldMetric(
            coverage=v,
            valid_count=int(v * 10),
            empty_count=10 - int(v * 10),
        )
        for k, v in coverage.items()
    }
    return ValidationResult(
        health_score=health,
        quality_score=quality,
        status="healthy" if health >= 0.80 else "broken",
        record_count=10,
        field_metrics=field_metrics,
        duplicate_metrics=DuplicateMetric(
            total_records=10, unique_records=10, duplicate_rate=dup_rate
        ),
        url_metrics=UrlMetric(total_urls=10, valid_urls=10, valid_rate=1.0),
        schema_metrics=SchemaMetric(
            valid_records=10, invalid_records=0, valid_rate=schema_valid
        ),
        failures=failures or [],
    )


def test_evaluator_accepts_healthy_transition():
    before = _make_val_result(
        health=0.35,
        quality=0.40,
        coverage={"title": 0.2, "price": 0.0},
        failures=[
            FailureItem(
                failure_type=FailureTaxonomy.LOW_FIELD_COVERAGE,
                severity="critical",
                message="Title missing",
            )
        ],
    )
    after = _make_val_result(
        health=0.88,
        quality=0.85,
        coverage={"title": 1.0, "price": 0.9},
        failures=[],
    )
    diagnosis = DiagnosisResult(root_cause=RootCause.SELECTOR_DRIFT, confidence=0.9)
    plan = RepairPlan(
        repair_type=RepairType.REPAIR_CSS_SELECTORS, reason="Fixed title selector"
    )

    evaluator = RepairEvaluator()
    evaluation = evaluator.evaluate(
        before=before, after=after, diagnosis=diagnosis, plan=plan
    )

    assert evaluation.accepted is True
    assert evaluation.improvement == pytest.approx(0.53)
    assert evaluation.critical_failure_resolved is True
    assert evaluation.regression_detected is False


def test_evaluator_accepts_small_healthy_bump():
    # Before 0.86, After 0.94 (+0.08 improvement, crosses healthy threshold)
    before = _make_val_result(
        health=0.86,
        quality=0.85,
        coverage={"title": 0.9, "price": 0.8},
    )
    after = _make_val_result(
        health=0.94,
        quality=0.92,
        coverage={"title": 1.0, "price": 0.95},
    )
    diagnosis = DiagnosisResult(root_cause=RootCause.SELECTOR_DRIFT, confidence=0.8)
    plan = RepairPlan(
        repair_type=RepairType.REPAIR_CSS_SELECTORS, reason="Refined price selector"
    )

    evaluator = RepairEvaluator()
    evaluation = evaluator.evaluate(
        before=before, after=after, diagnosis=diagnosis, plan=plan
    )

    assert evaluation.accepted is True
    assert evaluation.improvement == pytest.approx(0.08)


def test_evaluator_rejects_regression_in_healthy_field():
    before = _make_val_result(
        health=0.60,
        quality=0.65,
        coverage={"title": 0.95, "price": 0.20, "rating": 0.90},
    )
    # Price improves to 0.95, but rating drops drastically from 0.90 to 0.30
    after = _make_val_result(
        health=0.68,
        quality=0.65,
        coverage={"title": 0.95, "price": 0.95, "rating": 0.30},
    )
    diagnosis = DiagnosisResult(root_cause=RootCause.SELECTOR_DRIFT, confidence=0.8)
    plan = RepairPlan(
        repair_type=RepairType.REPAIR_CSS_SELECTORS,
        reason="Updated container and price",
    )

    evaluator = RepairEvaluator()
    evaluation = evaluator.evaluate(
        before=before, after=after, diagnosis=diagnosis, plan=plan
    )

    assert evaluation.accepted is False
    assert evaluation.regression_detected is True
    assert "rating" in evaluation.rejection_reason


def test_evaluator_rejects_duplicate_explosion():
    before = _make_val_result(
        health=0.30,
        quality=0.35,
        coverage={"title": 0.3},
        dup_rate=0.0,
    )
    after = _make_val_result(
        health=0.65,
        quality=0.50,
        coverage={"title": 0.9},
        dup_rate=0.45,  # Duplicate explosion
    )
    diagnosis = DiagnosisResult(root_cause=RootCause.SELECTOR_DRIFT, confidence=0.8)
    plan = RepairPlan(
        repair_type=RepairType.REPAIR_CSS_SELECTORS, reason="Loosened selector"
    )

    evaluator = RepairEvaluator()
    evaluation = evaluator.evaluate(
        before=before, after=after, diagnosis=diagnosis, plan=plan
    )

    assert evaluation.accepted is False
    assert evaluation.regression_detected is True
    assert "duplicate" in evaluation.rejection_reason.lower()


def test_evaluator_rejects_insufficient_improvement():
    before = _make_val_result(
        health=0.30,
        quality=0.35,
        coverage={"title": 0.3},
    )
    after = _make_val_result(
        health=0.34,  # Only +0.04 and still broken (0.34 < 0.80)
        quality=0.36,
        coverage={"title": 0.35},
    )
    diagnosis = DiagnosisResult(root_cause=RootCause.SELECTOR_DRIFT, confidence=0.8)
    plan = RepairPlan(repair_type=RepairType.REPAIR_CSS_SELECTORS, reason="Small tweak")

    evaluator = RepairEvaluator()
    evaluation = evaluator.evaluate(
        before=before, after=after, diagnosis=diagnosis, plan=plan
    )

    assert evaluation.accepted is False
    assert evaluation.regression_detected is False
    assert "Insufficient health improvement" in evaluation.rejection_reason
