import json
import pytest
from leadfinder.extraction.engine import ExtractionEngine
from leadfinder.extraction.schema import ExtractionSchema, ExtractionStrategyEnum, FieldRule
from leadfinder.models.schemas import ScrapingTask
from leadfinder.tests.conftest import MockLLMClient


@pytest.mark.asyncio
async def test_engine_passthrough_structured_records():
    engine = ExtractionEngine()
    task = ScrapingTask(
        task_id="t1",
        objective="Scrape items",
        target_urls=["https://example.com"],
        fields=["name", "price"],
    )
    raw = [{"name": "Alpha", "price": "$10"}, {"name": "Beta", "price": "$20"}]

    result = await engine.extract_async(raw, task)
    assert result.strategy_used == "passthrough"
    assert len(result.records) == 2
    assert result.records[0]["name"] == "Alpha"


@pytest.mark.asyncio
async def test_engine_css_selection():
    engine = ExtractionEngine()
    task = ScrapingTask(
        task_id="t2",
        objective="Scrape cards",
        target_urls=["https://example.com"],
        fields=["title", "price"],
    )
    html = """
    <div class="card">
        <h3 class="name">Product X</h3>
        <span class="cost">$99</span>
    </div>
    """
    schema = ExtractionSchema(
        base_selector=".card",
        fields=[
            FieldRule(name="title", selector=".name"),
            FieldRule(name="price", selector=".cost"),
        ],
    )

    result = await engine.extract_async(html, task, schema)
    assert result.strategy_used == "css"
    assert len(result.records) == 1
    assert result.records[0]["title"] == "Product X"


@pytest.mark.asyncio
async def test_engine_table_selection():
    engine = ExtractionEngine()
    task = ScrapingTask(
        task_id="t3",
        objective="Scrape table",
        target_urls=["https://example.com"],
        fields=["rank", "score"],
    )
    html = """
    <table>
        <tr><th>Rank</th><th>Score</th></tr>
        <tr><td>1</td><td>100</td></tr>
        <tr><td>2</td><td>95</td></tr>
    </table>
    """

    result = await engine.extract_async(html, task)
    assert result.strategy_used == "table"
    assert len(result.records) == 2


@pytest.mark.asyncio
async def test_engine_llm_fallback():
    mock_llm = MockLLMClient(response_text=json.dumps([{"summary": "Extracted with LLM"}]))
    engine = ExtractionEngine(llm_client=mock_llm)
    task = ScrapingTask(
        task_id="t4",
        objective="Summarize content",
        target_urls=["https://example.com"],
        fields=["summary"],
    )
    raw_text = "Plain unformatted paragraph of text describing a product."

    result = await engine.extract_async(raw_text, task)
    assert result.strategy_used == "llm"
    assert result.fallback_used is True
    assert len(result.records) == 1
    assert result.records[0]["summary"] == "Extracted with LLM"


@pytest.mark.asyncio
async def test_engine_filters_orphaned_records_without_primary_key():
    engine = ExtractionEngine()
    task = ScrapingTask(
        task_id="t5",
        objective="Scrape product listings",
        target_urls=["https://example.com/search"],
        fields=["name", "price", "rating"],
        is_list=True,
    )
    raw_records = [
        {"name": "iPhone 15", "price": "₹79,900", "rating": "4.6"},
        {"name": "Samsung S24", "price": "₹74,999", "rating": "4.5"},
        {"name": None, "price": "₹4,000", "rating": None},  # Orphaned carousel price
        {"name": None, "price": "₹230", "rating": None},    # Orphaned footer price
    ]
    result = await engine.extract_async(raw_records, task)
    # Orphaned records must be filtered out
    assert len(result.records) == 2
    assert result.records[0]["name"] == "iPhone 15"
    assert result.records[1]["name"] == "Samsung S24"

