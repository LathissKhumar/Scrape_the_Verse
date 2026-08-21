import pytest
from unittest.mock import AsyncMock, MagicMock
from leadfinder.diagnosis.schemas import DiagnosisResult, RootCause
from leadfinder.extraction.schema import ExtractionSchema, ExtractionStrategyEnum, FieldRule, RawPage
from leadfinder.healing.memory import RepairMemory
from leadfinder.healing.planner import HealingPlanner
from leadfinder.healing.schemas import RepairMemoryRecord, RepairType
from leadfinder.models.schemas import ScrapingTask
from leadfinder.validation.schemas import ValidationResult


@pytest.mark.asyncio
async def test_planner_scores_and_ranks_candidates():
    planner = HealingPlanner()
    task = ScrapingTask(task_id="t1", objective="Scrape laptops", target_urls=["https://example.com"])
    diagnosis = DiagnosisResult(
        root_cause=RootCause.SELECTOR_DRIFT,
        confidence=0.90,
        affected_fields=["price"],
    )
    validation = ValidationResult(status="broken", health_score=0.30)
    raw_pages = [RawPage(url="https://example.com", html="<div class='item'><h2>Laptop</h2><span class='cost'>$999</span></div>")]
    current_schema = ExtractionSchema(
        strategy=ExtractionStrategyEnum.CSS,
        base_selector=".old-item",
        fields=[FieldRule(name="title", selector="h2"), FieldRule(name="price", selector=".old-cost")],
    )

    candidates = await planner.generate_candidates(
        task=task,
        diagnosis=diagnosis,
        validation=validation,
        raw_pages=raw_pages,
        current_schema=current_schema,
    )

    assert len(candidates) > 0
    assert candidates[0].rank == 1
    # Ranked by score descending
    for i in range(len(candidates) - 1):
        assert candidates[i].score >= candidates[i + 1].score


@pytest.mark.asyncio
async def test_planner_seeds_candidate_from_memory():
    memory = RepairMemory()
    sig = memory.generate_signature(
        url="https://example.com",
        html="<div class='item'><h2>Laptop</h2></div>",
        fields=["title"],
    )
    memory.record_success(
        RepairMemoryRecord(
            domain="example.com",
            signature=sig,
            root_cause="SELECTOR_DRIFT",
            repair_type=RepairType.REPAIR_CSS_SELECTORS,
            successful_patch={"title": "h2"},
            health_before=0.30,
            health_after=0.95,
            strategy="css",
        )
    )

    planner = HealingPlanner(memory=memory)
    task = ScrapingTask(task_id="t1", objective="Scrape laptops", target_urls=["https://example.com"])
    diagnosis = DiagnosisResult(root_cause=RootCause.SELECTOR_DRIFT, confidence=0.85)
    validation = ValidationResult(status="broken", health_score=0.30)
    raw_pages = [RawPage(url="https://example.com", html="<div class='item'><h2>Laptop</h2></div>")]
    current_schema = ExtractionSchema(strategy=ExtractionStrategyEnum.CSS, fields=[FieldRule(name="title", selector=".bad")])

    candidates = await planner.generate_candidates(
        task=task,
        diagnosis=diagnosis,
        validation=validation,
        raw_pages=raw_pages,
        current_schema=current_schema,
    )

    memory_candidates = [c for c in candidates if c.source == "memory"]
    assert len(memory_candidates) == 1
    assert memory_candidates[0].plan.repair_type == RepairType.REPAIR_CSS_SELECTORS


@pytest.mark.asyncio
async def test_planner_invokes_llm_for_selector_repair():
    mock_llm = MagicMock()
    mock_llm.invoke = AsyncMock(return_value="""
    {
        "repair_type": "REPAIR_CSS_SELECTORS",
        "target_component": "extraction",
        "affected_fields": ["price"],
        "proposed_configuration": {"price": ".cost"},
        "patch": {"fields": [{"name": "price", "selector": ".cost"}]},
        "reason": "DOM contains .cost class for price",
        "confidence": 0.95,
        "expected_improvement": {"price_coverage": 0.95},
        "risk_level": "low"
    }
    """)

    planner = HealingPlanner(llm_client=mock_llm)
    task = ScrapingTask(task_id="t1", objective="Scrape products", target_urls=["https://example.com"])
    diagnosis = DiagnosisResult(root_cause=RootCause.SELECTOR_DRIFT, confidence=0.9, affected_fields=["price"])
    validation = ValidationResult(status="broken", health_score=0.3)
    raw_pages = [RawPage(url="https://example.com", html="<div class='product'><span class='cost'>$50</span></div>")]
    current_schema = ExtractionSchema(strategy=ExtractionStrategyEnum.CSS, fields=[FieldRule(name="price", selector=".old-price")])

    candidates = await planner.generate_candidates(
        task=task,
        diagnosis=diagnosis,
        validation=validation,
        raw_pages=raw_pages,
        current_schema=current_schema,
    )

    assert any(c.plan.proposed_configuration.get("price") == ".cost" for c in candidates)
    mock_llm.invoke.assert_awaited_once()
