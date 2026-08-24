from leadfinder.healing.schemas import (
    PerformanceSnapshot,
    RepairCandidate,
    RepairEvaluation,
    RepairMemoryRecord,
    RepairPlan,
    RepairStatus,
    RepairType,
)


def test_repair_type_and_status_enums():
    assert RepairType.REPAIR_CSS_SELECTORS == "REPAIR_CSS_SELECTORS"
    assert RepairType.SWITCH_EXTRACTION_STRATEGY == "SWITCH_EXTRACTION_STRATEGY"
    assert RepairType.NO_REPAIR_REQUIRED == "NO_REPAIR_REQUIRED"
    assert RepairType.ESCALATE == "ESCALATE"
    assert RepairStatus.ACCEPTED == "accepted"


def test_performance_snapshot():
    snapshot = PerformanceSnapshot(
        health=0.85,
        quality=0.90,
        records=25,
        field_coverage={"name": 1.0, "price": 0.8},
        duplicate_rate=0.04,
        schema_valid_rate=0.96,
        strategy_used="css",
    )
    assert snapshot.health == 0.85
    assert snapshot.records == 25
    assert snapshot.field_coverage["name"] == 1.0


def test_repair_plan_validation():
    plan = RepairPlan(
        repair_type=RepairType.REPAIR_CSS_SELECTORS,
        target_component="extraction",
        affected_fields=["price"],
        previous_configuration={"price": ".old-price"},
        proposed_configuration={"price": ".new-price"},
        patch={"fields": [{"name": "price", "selector": ".new-price"}]},
        reason="Price selector drifted",
        confidence=0.92,
        expected_improvement={"price_coverage": 0.95},
        test_requirements=["price coverage >= 0.90"],
        risk_level="low",
        level=1,
    )
    assert plan.repair_id is not None
    assert plan.repair_type == RepairType.REPAIR_CSS_SELECTORS
    assert plan.confidence == 0.92
    assert plan.level == 1


def test_repair_candidate_scoring():
    plan = RepairPlan(
        repair_type=RepairType.REPAIR_CSS_SELECTORS,
        reason="Test",
        confidence=0.85,
    )
    candidate = RepairCandidate(
        plan=plan,
        score=0.82,
        rank=1,
        source="planner_llm",
    )
    assert candidate.score == 0.82
    assert candidate.rank == 1


def test_repair_evaluation_model():
    before = PerformanceSnapshot(health=0.30, quality=0.35, records=5)
    after = PerformanceSnapshot(health=0.92, quality=0.90, records=50)

    evaluation = RepairEvaluation(
        repair_id="rep-123",
        before=before,
        after=after,
        improvement=0.62,
        critical_failure_resolved=True,
        regression_detected=False,
        accepted=True,
    )
    assert evaluation.accepted is True
    assert evaluation.improvement == 0.62
    assert evaluation.rejection_reason is None


def test_repair_memory_record():
    record = RepairMemoryRecord(
        domain="books.toscrape.com",
        signature="sig_12345",
        root_cause="SELECTOR_DRIFT",
        repair_type=RepairType.REPAIR_CSS_SELECTORS,
        successful_patch={"title": "h3 a"},
        health_before=0.30,
        health_after=0.95,
        strategy="css",
        provider="local",
    )
    assert record.domain == "books.toscrape.com"
    assert record.timestamp is not None
