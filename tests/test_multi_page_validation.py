import pytest
from unittest.mock import AsyncMock, MagicMock
from app.extraction.schema import ExtractionResult, ExtractionSchema, RawPage
from app.healing.multi_page import MultiPageRepairValidator
from app.models.schemas import ScrapingTask
from app.validation.schemas import ValidationResult


@pytest.mark.asyncio
async def test_multi_page_validator_passes_when_consistent():
    mock_extractor = MagicMock()
    mock_extractor.extract_async = AsyncMock(
        return_value=ExtractionResult(records=[{"title": "Prod 1"}, {"title": "Prod 2"}], strategy_used="css")
    )
    mock_validator = MagicMock()
    mock_validator.validate.return_value = ValidationResult(status="healthy", health_score=0.95)

    multi_page_val = MultiPageRepairValidator(
        extraction_engine=mock_extractor,
        validation_engine=mock_validator,
    )

    task = ScrapingTask(task_id="t1", objective="scrape", target_urls=["https://example.com/p1", "https://example.com/p2"])
    schema = ExtractionSchema()
    pages = [
        RawPage(url="https://example.com/p1", html="<html>Page 1</html>"),
        RawPage(url="https://example.com/p2", html="<html>Page 2</html>"),
    ]

    passed, avg_health, metrics, reason = await multi_page_val.validate_candidate_across_pages(
        task=task, schema=schema, raw_pages=pages
    )

    assert passed is True
    assert avg_health >= 0.90
    assert len(metrics) == 2
    assert reason is None


@pytest.mark.asyncio
async def test_multi_page_validator_rejects_when_inconsistent():
    mock_extractor = MagicMock()
    mock_extractor.extract_async = AsyncMock(
        return_value=ExtractionResult(records=[{"title": "Prod 1"}], strategy_used="css")
    )
    mock_validator = MagicMock()
    # First page healthy (0.90), second page broken (0.20)
    mock_validator.validate.side_effect = [
        ValidationResult(status="healthy", health_score=0.90),
        ValidationResult(status="broken", health_score=0.20),
    ]

    multi_page_val = MultiPageRepairValidator(
        extraction_engine=mock_extractor,
        validation_engine=mock_validator,
    )

    task = ScrapingTask(task_id="t1", objective="scrape", target_urls=["https://example.com/p1", "https://example.com/p2"])
    schema = ExtractionSchema()
    pages = [
        RawPage(url="https://example.com/p1", html="<html>Page 1</html>"),
        RawPage(url="https://example.com/p2", html="<html>Page 2</html>"),
    ]

    passed, avg_health, metrics, reason = await multi_page_val.validate_candidate_across_pages(
        task=task, schema=schema, raw_pages=pages
    )

    assert passed is False
    assert "Multi-page inconsistency" in str(reason)
