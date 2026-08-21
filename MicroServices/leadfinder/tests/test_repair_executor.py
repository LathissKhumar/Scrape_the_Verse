import pytest
from leadfinder.extraction.schema import ExtractionSchema, ExtractionStrategyEnum, FieldRule
from leadfinder.healing.executor import RepairExecutor
from leadfinder.healing.schemas import RepairPlan, RepairType


def test_executor_applies_level1_extraction_patch():
    executor = RepairExecutor()
    schema = ExtractionSchema(
        strategy=ExtractionStrategyEnum.CSS,
        fields=[FieldRule(name="title", selector=".old-title")],
    )
    plan = RepairPlan(
        repair_type=RepairType.REPAIR_CSS_SELECTORS,
        target_component="extraction",
        affected_fields=["title"],
        proposed_configuration={"title": ".new-title"},
        patch={"fields": [{"name": "title", "selector": ".new-title"}]},
        reason="Updated title selector",
        level=1,
    )

    new_schema, scraper_config = executor.apply_candidate(plan=plan, schema=schema)
    assert new_schema.fields[0].selector == ".new-title"
    assert new_schema.strategy == ExtractionStrategyEnum.CSS


def test_executor_applies_level2_scraper_config():
    executor = RepairExecutor()
    schema = ExtractionSchema(strategy=ExtractionStrategyEnum.CSS)
    plan = RepairPlan(
        repair_type=RepairType.REPAIR_SCRAPER_CONFIG,
        target_component="scraper",
        proposed_configuration={"headers": {"User-Agent": "CustomAgent/1.0"}},
        patch={"headers": {"User-Agent": "CustomAgent/1.0"}},
        reason="Update User-Agent header",
        level=2,
    )

    new_schema, scraper_config = executor.apply_candidate(
        plan=plan,
        schema=schema,
        scraper_config={"timeout": 30},
    )
    assert scraper_config["headers"]["User-Agent"] == "CustomAgent/1.0"
    assert scraper_config["timeout"] == 30


def test_executor_handles_level3_brightdata_fallback():
    executor = RepairExecutor()
    schema = ExtractionSchema(strategy=ExtractionStrategyEnum.CSS)
    plan = RepairPlan(
        repair_type=RepairType.BRIGHTDATA_REFACTOR_FALLBACK,
        target_component="collector",
        proposed_configuration={"collector_id": "c_healed_123"},
        reason="Fallback to Bright Data self-healed collector",
        level=3,
    )

    new_schema, scraper_config = executor.apply_candidate(plan=plan, schema=schema)
    assert scraper_config.get("candidate_collector_id") == "c_healed_123"
