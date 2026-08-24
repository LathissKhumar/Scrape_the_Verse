from leadfinder.extraction.schema import (
    ExtractionSchema,
    ExtractionStrategyEnum,
    FieldRule,
)
from leadfinder.healing.patcher import RepairPatcher
from leadfinder.healing.schemas import RepairPlan, RepairType


def test_patch_css_field_selector():
    original_schema = ExtractionSchema(
        strategy=ExtractionStrategyEnum.CSS,
        base_selector=".product-card",
        fields=[
            FieldRule(name="title", selector=".old-title"),
            FieldRule(name="price", selector=".old-price"),
        ],
    )

    plan = RepairPlan(
        repair_type=RepairType.REPAIR_CSS_SELECTORS,
        target_component="extraction",
        affected_fields=["price"],
        reason="Price selector changed to .current-price",
        patch={
            "fields": [{"name": "price", "selector": ".current-price"}],
        },
    )

    patched = RepairPatcher.apply_patch(schema=original_schema, plan=plan)

    # Title is untouched
    title_rule = next(f for f in patched.fields if f.name == "title")
    assert title_rule.selector == ".old-title"

    # Price is updated
    price_rule = next(f for f in patched.fields if f.name == "price")
    assert price_rule.selector == ".current-price"
    assert patched.base_selector == ".product-card"


def test_patch_base_selector():
    original_schema = ExtractionSchema(
        strategy=ExtractionStrategyEnum.CSS,
        base_selector=".old-container",
        fields=[FieldRule(name="title", selector="h2")],
    )

    plan = RepairPlan(
        repair_type=RepairType.REPAIR_CSS_SELECTORS,
        target_component="extraction",
        reason="Container updated",
        patch={"base_selector": ".new-container"},
    )

    patched = RepairPatcher.apply_patch(schema=original_schema, plan=plan)
    assert patched.base_selector == ".new-container"
    assert patched.fields[0].selector == "h2"


def test_patch_switch_extraction_strategy():
    original_schema = ExtractionSchema(
        strategy=ExtractionStrategyEnum.CSS,
        fields=[FieldRule(name="title", selector=".title")],
    )

    plan = RepairPlan(
        repair_type=RepairType.SWITCH_EXTRACTION_STRATEGY,
        target_component="extraction",
        reason="CSS failed, switch to semantic",
        patch={"strategy": "semantic"},
    )

    patched = RepairPatcher.apply_patch(schema=original_schema, plan=plan)
    assert patched.strategy == ExtractionStrategyEnum.SEMANTIC


def test_patch_regex_pattern():
    original_schema = ExtractionSchema(
        strategy=ExtractionStrategyEnum.REGEX,
        fields=[FieldRule(name="phone", regex_pattern=r"\d{3}-\d{4}")],
    )

    plan = RepairPlan(
        repair_type=RepairType.REPAIR_REGEX_PATTERN,
        target_component="extraction",
        affected_fields=["phone"],
        reason="Phone format changed to international",
        patch={
            "fields": [{"name": "phone", "regex_pattern": r"\+\d{1,3}-\d{3}-\d{4}"}]
        },
    )

    patched = RepairPatcher.apply_patch(schema=original_schema, plan=plan)
    assert patched.fields[0].regex_pattern == r"\+\d{1,3}-\d{3}-\d{4}"


def test_patch_xpath_selector():
    original_schema = ExtractionSchema(
        strategy=ExtractionStrategyEnum.XPATH,
        base_selector="//div[@class='card']",
        fields=[FieldRule(name="title", selector=".//h2/text()")],
    )

    plan = RepairPlan(
        repair_type=RepairType.REPAIR_XPATH_SELECTORS,
        target_component="extraction",
        affected_fields=["title"],
        reason="Update title xpath",
        patch={"fields": [{"name": "title", "selector": ".//h3/a/text()"}]},
    )

    patched = RepairPatcher.apply_patch(schema=original_schema, plan=plan)
    assert patched.fields[0].selector == ".//h3/a/text()"
