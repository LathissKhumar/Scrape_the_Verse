from leadfinder.diagnosis.schemas import (
    AffectedStage,
    DiagnosisResult,
    RecommendedAction,
    RepairStrategy,
    RootCause,
)


def test_diagnosis_result_instantiation():
    result = DiagnosisResult(
        diagnosis_status="diagnosed",
        root_cause=RootCause.SELECTOR_DRIFT,
        confidence=0.94,
        failure_category="EXTRACTION_DEGRADATION",
        affected_stage=AffectedStage.CSS_EXTRACTION,
        affected_fields=["product_name", "price"],
        evidence=["Record count dropped from 100 to 5", "Classes renamed"],
        repair_strategy=RepairStrategy.REPAIR_CSS_SELECTORS,
        repair_targets=["product_name", "price"],
        recommended_action=RecommendedAction.REPAIR_EXTRACTION_SCHEMA,
    )

    assert result.root_cause == RootCause.SELECTOR_DRIFT
    assert result.confidence == 0.94
    assert result.repair_strategy == RepairStrategy.REPAIR_CSS_SELECTORS
    assert result.affected_stage == AffectedStage.CSS_EXTRACTION
