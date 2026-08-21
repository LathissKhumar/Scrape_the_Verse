from leadfinder.validation.health import HealthScorer
from leadfinder.validation.schemas import (
    DuplicateMetric,
    FieldMetric,
    SchemaMetric,
    UrlMetric,
)


def test_health_scorer_healthy_scenario():
    scorer = HealthScorer()
    field_metrics = {
        "name": FieldMetric(coverage=1.0, valid_count=100),
        "price": FieldMetric(coverage=0.98, valid_count=98),
    }
    dup_metrics = DuplicateMetric(
        total_records=100,
        unique_records=99,
        duplicate_records=1,
        duplicate_rate=0.01,
    )
    url_metrics = UrlMetric(total_urls=100, valid_urls=100, valid_rate=1.0)
    schema_metrics = SchemaMetric(valid_records=100, valid_rate=1.0)

    health, quality, status = scorer.calculate_health_score(
        record_count=100,
        field_metrics=field_metrics,
        duplicate_metrics=dup_metrics,
        url_metrics=url_metrics,
        schema_metrics=schema_metrics,
        expected_max_records=100,
    )

    assert health >= 0.85
    assert quality >= 0.85
    assert status == "healthy"


def test_health_scorer_broken_scenario():
    scorer = HealthScorer()
    health, quality, status = scorer.calculate_health_score(
        record_count=0,
        field_metrics={},
        duplicate_metrics=DuplicateMetric(),
        url_metrics=UrlMetric(),
        schema_metrics=SchemaMetric(),
    )
    assert health == 0.0
    assert status == "broken"
