import pytest
from unittest.mock import AsyncMock, MagicMock
from leadfinder.diagnosis.schemas import DiagnosisResult, RootCause
from leadfinder.extraction.schema import (
    ExtractionResult,
    ExtractionSchema,
    ExtractionStrategyEnum,
    FieldRule,
    RawPage,
)
from leadfinder.healing.engine import HealingEngine
from leadfinder.healing.evaluator import RepairEvaluator
from leadfinder.healing.evidence_collector import RepairEvidenceCollector
from leadfinder.healing.executor import RepairExecutor
from leadfinder.healing.memory import RepairMemory
from leadfinder.healing.patcher import RepairPatcher
from leadfinder.healing.planner import HealingPlanner
from leadfinder.healing.schemas import RepairCandidate, RepairPlan, RepairType
from leadfinder.models.schemas import ScrapingTask
from leadfinder.validation.engine import ValidationEngine
from leadfinder.validation.schemas import (
    FailureItem,
    FailureTaxonomy,
    FieldMetric,
    ValidationResult,
)


@pytest.mark.asyncio
async def test_case_1_css_selector_drift_end_to_end():
    """Case 1: CSS selector drifted after site layout redesign.

    Old: .product-card .title, .price
    New: .product-item .product-name, .current-price
    """
    new_html = """
    <html>
        <body>
            <div class="product-item">
                <h2 class="product-name">MacBook Pro 16</h2>
                <span class="current-price">$2499</span>
            </div>
            <div class="product-item">
                <h2 class="product-name">Dell XPS 15</h2>
                <span class="current-price">$1899</span>
            </div>
        </body>
    </html>
    """
    task = ScrapingTask(
        task_id="case_1_drift",
        objective="Scrape laptops",
        target_urls=["https://store.example.com/laptops"],
        fields=["product_name", "price"],
    )

    old_schema = ExtractionSchema(
        strategy=ExtractionStrategyEnum.CSS,
        base_selector=".product-card",
        fields=[
            FieldRule(name="product_name", selector=".title"),
            FieldRule(name="price", selector=".price"),
        ],
    )

    mock_scraper = MagicMock()
    mock_scraper.execute = AsyncMock(return_value=[{"html": new_html, "url": "https://store.example.com/laptops"}])

    mock_llm = MagicMock()
    mock_llm.invoke = AsyncMock(return_value="""
    {
        "repair_type": "REPAIR_CSS_SELECTORS",
        "target_component": "extraction",
        "affected_fields": ["product_name", "price"],
        "proposed_configuration": {
            "base_selector": ".product-item",
            "product_name": ".product-name",
            "price": ".current-price"
        },
        "patch": {
            "base_selector": ".product-item",
            "fields": [
                {"name": "product_name", "selector": ".product-name"},
                {"name": "price", "selector": ".current-price"}
            ]
        },
        "reason": "DOM updated container to .product-item and classes to .product-name and .current-price",
        "confidence": 0.95,
        "expected_improvement": {"product_name_coverage": 1.0, "price_coverage": 1.0},
        "risk_level": "low"
    }
    """)

    validation_engine = ValidationEngine()
    planner = HealingPlanner(llm_client=mock_llm)
    collector = RepairEvidenceCollector(scraper_agent=mock_scraper)
    engine = HealingEngine(
        evidence_collector=collector,
        planner=planner,
        validation_engine=validation_engine,
    )

    # Initial broken validation
    initial_val = ValidationResult(
        health_score=0.0,
        quality_score=0.0,
        status="broken",
        record_count=0,
        failures=[
            FailureItem(failure_type=FailureTaxonomy.EMPTY_RESULTS, severity="critical", message="Zero records extracted")
        ],
    )
    diagnosis = DiagnosisResult(
        root_cause=RootCause.SELECTOR_DRIFT,
        confidence=0.92,
        affected_fields=["product_name", "price"],
    )

    success, healed_schema, evaluation, records, history = await engine.heal(
        task=task,
        diagnosis=diagnosis,
        validation=initial_val,
        current_schema=old_schema,
    )

    assert success is True
    assert evaluation.accepted is True
    assert evaluation.before.health == 0.0
    assert evaluation.after.health >= 0.85
    assert len(records) == 2
    assert records[0]["product_name"] == "MacBook Pro 16"
    assert records[0]["price"] == "$2499"
    assert healed_schema.base_selector == ".product-item"


@pytest.mark.asyncio
async def test_case_2_strategy_switch_css_to_semantic_llm():
    """Case 2: CSS completely fails, strategy switches to semantic/llm and recovers records."""
    raw_html = "<p>Featured Book: <b>The Great Gatsby</b> written by F. Scott Fitzgerald. Cost is $12.</p>"
    task = ScrapingTask(
        task_id="case_2_switch",
        objective="Scrape books",
        target_urls=["https://example.com/books"],
        fields=["title", "author", "price"],
    )
    old_schema = ExtractionSchema(strategy=ExtractionStrategyEnum.CSS, base_selector=".nonexistent")

    mock_scraper = MagicMock()
    mock_scraper.execute = AsyncMock(return_value=[{"html": raw_html, "url": "https://example.com/books"}])

    mock_extractor = MagicMock()
    mock_extractor.extract = AsyncMock(
        return_value=ExtractionResult(
            records=[{"title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "price": "$12"}],
            strategy_used="semantic",
        )
    )

    mock_validator = MagicMock()
    mock_validator.validate = AsyncMock(
        return_value=ValidationResult(
            health_score=0.92,
            quality_score=0.90,
            status="healthy",
            record_count=1,
            field_metrics={
                "title": FieldMetric(coverage=1.0, valid_count=1),
                "author": FieldMetric(coverage=1.0, valid_count=1),
                "price": FieldMetric(coverage=1.0, valid_count=1),
            },
        )
    )

    engine = HealingEngine(
        evidence_collector=RepairEvidenceCollector(scraper_agent=mock_scraper),
        extraction_engine=mock_extractor,
        validation_engine=mock_validator,
    )

    initial_val = ValidationResult(health_score=0.20, status="broken", record_count=0)
    diagnosis = DiagnosisResult(root_cause=RootCause.SELECTOR_DRIFT, confidence=0.85)

    success, healed_schema, evaluation, records, history = await engine.heal(
        task=task,
        diagnosis=diagnosis,
        validation=initial_val,
        current_schema=old_schema,
    )

    assert success is True
    assert evaluation.accepted is True
    assert healed_schema.strategy in (ExtractionStrategyEnum.SEMANTIC, ExtractionStrategyEnum.LLM)
    assert len(records) == 1
    assert records[0]["title"] == "The Great Gatsby"


@pytest.mark.asyncio
async def test_case_3_regex_pattern_drift():
    """Case 3: Regex pattern drifted and requires pattern repair."""
    text_content = "Contact support at +1-800-555-0199 or +44-20-7946-0912"
    task = ScrapingTask(
        task_id="case_3_regex",
        objective="Extract phone numbers",
        target_urls=["https://example.com/contact"],
        fields=["phone"],
    )
    old_schema = ExtractionSchema(
        strategy=ExtractionStrategyEnum.REGEX,
        fields=[FieldRule(name="phone", regex_pattern=r"^\d{3}-\d{4}$")],  # Old 7-digit pattern fails
    )

    mock_scraper = MagicMock()
    mock_scraper.execute = AsyncMock(return_value=[{"text": text_content, "url": "https://example.com/contact"}])

    mock_llm = MagicMock()
    mock_llm.invoke = AsyncMock(return_value="""
    {
        "repair_type": "REPAIR_REGEX_PATTERN",
        "target_component": "extraction",
        "affected_fields": ["phone"],
        "proposed_configuration": {"phone": "\\\\+\\\\d{1,2}-\\\\d{3}-\\\\d{3}-\\\\d{4}"},
        "patch": {"fields": [{"name": "phone", "regex_pattern": "\\\\+\\\\d{1,2}-\\\\d{3}-\\\\d{3}-\\\\d{4}"}]},
        "reason": "Phone numbers contain international country codes",
        "confidence": 0.92,
        "risk_level": "low"
    }
    """)

    mock_extractor = MagicMock()
    mock_extractor.extract = AsyncMock(
        return_value=ExtractionResult(records=[{"phone": "+1-800-555-0199"}], strategy_used="regex")
    )
    mock_validator = MagicMock()
    mock_validator.validate = AsyncMock(
        return_value=ValidationResult(health_score=0.90, quality_score=0.90, status="healthy", record_count=1)
    )

    engine = HealingEngine(
        evidence_collector=RepairEvidenceCollector(scraper_agent=mock_scraper),
        planner=HealingPlanner(llm_client=mock_llm),
        extraction_engine=mock_extractor,
        validation_engine=mock_validator,
    )

    initial_val = ValidationResult(health_score=0.25, status="broken")
    diagnosis = DiagnosisResult(root_cause=RootCause.REGEX_PATTERN_FAILURE, confidence=0.88, affected_fields=["phone"])

    success, healed_schema, evaluation, records, history = await engine.heal(
        task=task,
        diagnosis=diagnosis,
        validation=initial_val,
        current_schema=old_schema,
    )

    assert success is True
    assert evaluation.accepted is True
    assert healed_schema.fields[0].regex_pattern is not None


@pytest.mark.asyncio
async def test_case_4_table_structure_repair():
    """Case 4: HTML table structure change repaired."""
    table_html = """
    <table>
        <thead><tr><th>Product</th><th>Price</th></tr></thead>
        <tbody>
            <tr><td>Monitor</td><td>$300</td></tr>
            <tr><td>Keyboard</td><td>$80</td></tr>
        </tbody>
    </table>
    """
    task = ScrapingTask(
        task_id="case_4_table",
        objective="Scrape table",
        target_urls=["https://example.com/table"],
        fields=["product", "price"],
    )
    old_schema = ExtractionSchema(strategy=ExtractionStrategyEnum.CSS, base_selector=".wrong-div")

    mock_scraper = MagicMock()
    mock_scraper.execute = AsyncMock(return_value=[{"html": table_html, "url": "https://example.com/table"}])

    mock_extractor = MagicMock()
    mock_extractor.extract = AsyncMock(
        return_value=ExtractionResult(
            records=[{"product": "Monitor", "price": "$300"}, {"product": "Keyboard", "price": "$80"}],
            strategy_used="table",
        )
    )
    mock_validator = MagicMock()
    mock_validator.validate = AsyncMock(
        return_value=ValidationResult(health_score=0.95, quality_score=0.95, status="healthy", record_count=2)
    )

    engine = HealingEngine(
        evidence_collector=RepairEvidenceCollector(scraper_agent=mock_scraper),
        extraction_engine=mock_extractor,
        validation_engine=mock_validator,
    )

    initial_val = ValidationResult(health_score=0.10, status="broken")
    diagnosis = DiagnosisResult(root_cause=RootCause.TABLE_STRUCTURE_CHANGE, confidence=0.9)

    success, healed_schema, evaluation, records, history = await engine.heal(
        task=task,
        diagnosis=diagnosis,
        validation=initial_val,
        current_schema=old_schema,
    )

    assert success is True
    assert evaluation.accepted is True
    assert len(records) == 2


@pytest.mark.asyncio
async def test_case_5_repeated_failures_escalate():
    """Case 6: Repeated failed repair candidates exhaust retry limit and escalate safely."""
    mock_scraper = MagicMock()
    mock_scraper.execute = AsyncMock(return_value=[{"html": "<div>Corrupted</div>", "url": "https://example.com"}])

    mock_extractor = MagicMock()
    mock_extractor.extract = AsyncMock(return_value=ExtractionResult(records=[], strategy_used="none"))

    mock_validator = MagicMock()
    mock_validator.validate = AsyncMock(return_value=ValidationResult(health_score=0.20, status="broken"))

    engine = HealingEngine(
        evidence_collector=RepairEvidenceCollector(scraper_agent=mock_scraper),
        extraction_engine=mock_extractor,
        validation_engine=mock_validator,
        max_repair_attempts=2,
    )

    task = ScrapingTask(task_id="case_6_esc", objective="Scrape", target_urls=["https://example.com"])
    diagnosis = DiagnosisResult(root_cause=RootCause.UNKNOWN, confidence=0.40)
    initial_val = ValidationResult(health_score=0.20, status="broken")
    current_schema = ExtractionSchema(strategy=ExtractionStrategyEnum.CSS)

    success, healed_schema, evaluation, records, history = await engine.heal(
        task=task,
        diagnosis=diagnosis,
        validation=initial_val,
        current_schema=current_schema,
    )

    assert success is False
    assert evaluation.accepted is False
    assert len(history) <= 2
