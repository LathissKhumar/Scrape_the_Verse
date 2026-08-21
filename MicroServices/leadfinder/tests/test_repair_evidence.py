import pytest
from unittest.mock import AsyncMock, MagicMock
from leadfinder.extraction.schema import ExtractionSchema, ExtractionStrategyEnum, FieldRule, RawPage
from leadfinder.healing.evidence_collector import RepairEvidenceCollector
from leadfinder.models.schemas import ScrapingTask
from leadfinder.validation.schemas import ValidationResult


@pytest.mark.asyncio
async def test_evidence_collector_fetches_fresh_pages():
    mock_scraper = MagicMock()
    mock_scraper.execute = AsyncMock(return_value=[
        {"url": "https://example.com/shop", "html": "<html><body><div class='item'>Laptop</div></body></html>"}
    ])

    collector = RepairEvidenceCollector(scraper_agent=mock_scraper)
    task = ScrapingTask(task_id="t1", objective="Scrape laptops", target_urls=["https://example.com/shop"])

    raw_pages = await collector.collect_fresh_pages(task=task)

    assert len(raw_pages) == 1
    assert "item" in raw_pages[0].get_primary_content()
    mock_scraper.execute.assert_awaited_once_with(task=task)


@pytest.mark.asyncio
async def test_evidence_collector_detects_transient_recovery():
    mock_scraper = MagicMock()
    mock_scraper.execute = AsyncMock(return_value=[
        {"url": "https://example.com", "html": "<div class='card'><h2 class='title'>Book</h2></div>"}
    ])

    mock_extractor = MagicMock()
    mock_extractor.extract = AsyncMock(return_value=MagicMock(records=[{"title": "Book"}], strategy_used="css"))

    mock_validator = MagicMock()
    mock_validator.validate = AsyncMock(return_value=ValidationResult(status="healthy", health_score=0.95))

    collector = RepairEvidenceCollector(
        scraper_agent=mock_scraper,
        extraction_engine=mock_extractor,
        validation_engine=mock_validator,
    )
    task = ScrapingTask(task_id="t1", objective="Scrape books", target_urls=["https://example.com"])
    schema = ExtractionSchema(strategy=ExtractionStrategyEnum.CSS, fields=[FieldRule(name="title", selector=".title")])

    raw_pages, is_recovered, val_res = await collector.check_transient_recovery(task=task, schema=schema)

    assert is_recovered is True
    assert val_res.health_score == 0.95


def test_evidence_collector_summarizes_dom():
    collector = RepairEvidenceCollector()
    raw_pages = [
        RawPage(
            url="https://example.com/products",
            html="""
            <html>
                <body>
                    <div class="product-item">
                        <h3 class="product-title">Item 1</h3>
                        <span class="product-price">$10</span>
                    </div>
                    <div class="product-item">
                        <h3 class="product-title">Item 2</h3>
                        <span class="product-price">$20</span>
                    </div>
                </body>
            </html>
            """,
        )
    ]

    summary = collector.summarize_dom_evidence(raw_pages=raw_pages)
    assert summary["sample_url"] == "https://example.com/products"
    assert "product-item" in summary["candidate_classes"]
    assert "product-title" in summary["candidate_classes"]
    assert len(summary["tag_counts"]) > 0
