from leadfinder.models.schemas import ScrapingTask
from leadfinder.validation.baseline import HistoricalBaseline
from leadfinder.validation.engine import ValidationEngine


def test_validation_engine_healthy_evaluation():
    engine = ValidationEngine()
    task = ScrapingTask(
        task_id="t_val_1",
        objective="Scrape books",
        target_urls=["https://example.com/books"],
        fields=["title", "price"],
        output_schema={"title": "string", "price": "string"},
    )
    records = [{"title": f"Book {i}", "price": f"${i * 5}"} for i in range(1, 51)]

    result = engine.validate(records=records, task=task)
    assert result.status == "healthy"
    assert result.health_score >= 0.85
    assert result.record_count == 50
    assert len(result.failures) == 0


def test_validation_engine_degraded_evaluation():
    engine = ValidationEngine()
    task = ScrapingTask(
        task_id="t_val_2",
        objective="Scrape companies",
        target_urls=["https://example.com/companies"],
        fields=["name", "ceo", "email"],
    )
    # email and ceo have low coverage
    records = [
        {
            "name": f"Company {i}",
            "ceo": "N/A" if i > 5 else "CEO",
            "email": None if i > 10 else "a@b.com",
        }
        for i in range(50)
    ]

    result = engine.validate(records=records, task=task)
    assert result.status in ("degraded", "unstable")
    assert result.health_score < 0.85
    assert len(result.failures) > 0


def test_validation_engine_baseline_deviation():
    engine = ValidationEngine()
    task = ScrapingTask(
        task_id="t_val_3",
        objective="Scrape news",
        target_urls=["https://example.com/news"],
        fields=["headline"],
    )
    # Only 5 records
    records = [{"headline": f"News {i}"} for i in range(5)]

    baseline = HistoricalBaseline(
        average_record_count=100.0,
        field_coverage={"headline": 1.0},
        run_count=5,
    )

    result = engine.validate(records=records, task=task, historical_baseline=baseline)
    assert any("drop" in a.lower() for a in result.anomalies)
