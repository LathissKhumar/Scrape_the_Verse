from app.validation.anomalies import AnomalyDetector
from app.validation.schemas import (
    DuplicateMetric,
    FailureTaxonomy,
    FieldMetric,
    SchemaMetric,
    UrlMetric,
)


def test_anomaly_zero_records_raw_missing():
    detector = AnomalyDetector()
    anomalies, failures = detector.detect_anomalies(
        records=[],
        field_metrics={},
        duplicate_metrics=DuplicateMetric(),
        url_metrics=UrlMetric(),
        schema_metrics=SchemaMetric(),
        raw_results=None,
    )
    assert len(anomalies) > 0
    assert len(failures) == 1
    assert failures[0].failure_type == FailureTaxonomy.SCRAPER_OUTPUT_MISSING


def test_anomaly_zero_records_raw_present():
    detector = AnomalyDetector()
    anomalies, failures = detector.detect_anomalies(
        records=[],
        field_metrics={},
        duplicate_metrics=DuplicateMetric(),
        url_metrics=UrlMetric(),
        schema_metrics=SchemaMetric(),
        raw_results="<html><body><div>Some content</div></body></html>",
    )
    assert len(anomalies) > 0
    assert len(failures) == 1
    assert failures[0].failure_type == FailureTaxonomy.EXTRACTION_DEGRADATION


def test_anomaly_coverage_collapse_and_duplicate_explosion():
    detector = AnomalyDetector()
    field_metrics = {
        "title": FieldMetric(coverage=0.95),
        "ceo": FieldMetric(coverage=0.10),
    }
    dup_metrics = DuplicateMetric(
        total_records=100,
        unique_records=60,
        duplicate_records=40,
        duplicate_rate=0.40,
    )
    anomalies, failures = detector.detect_anomalies(
        records=[{"title": "T"}] * 100,
        field_metrics=field_metrics,
        duplicate_metrics=dup_metrics,
        url_metrics=UrlMetric(),
        schema_metrics=SchemaMetric(),
    )

    failure_types = [f.failure_type for f in failures]
    assert FailureTaxonomy.LOW_FIELD_COVERAGE in failure_types
    assert FailureTaxonomy.HIGH_DUPLICATE_RATE in failure_types
