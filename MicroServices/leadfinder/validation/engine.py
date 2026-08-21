from typing import Any, Optional

from leadfinder.config.logging import get_logger
from leadfinder.models.schemas import ScrapingTask
from leadfinder.validation.anomalies import AnomalyDetector
from leadfinder.validation.baseline import HistoricalBaseline, compare_with_baseline
from leadfinder.validation.completeness import CompletenessValidator
from leadfinder.validation.duplicates import DuplicateValidator
from leadfinder.validation.health import HealthScorer
from leadfinder.validation.schemas import (
    DuplicateMetric,
    FieldMetric,
    SchemaMetric,
    UrlMetric,
    ValidationResult,
)
from leadfinder.validation.type_validator import TypeValidator
from leadfinder.validation.urls import URLValidator

logger = get_logger("VALIDATION_ENGINE")


class ValidationEngine:
    """Central deterministic validation engine evaluating data quality, health scores, and anomalies."""

    def __init__(
        self,
        completeness_validator: Optional[CompletenessValidator] = None,
        type_validator: Optional[TypeValidator] = None,
        url_validator: Optional[URLValidator] = None,
        duplicate_validator: Optional[DuplicateValidator] = None,
        anomaly_detector: Optional[AnomalyDetector] = None,
        health_scorer: Optional[HealthScorer] = None,
    ):
        self.completeness_validator = completeness_validator or CompletenessValidator()
        self.type_validator = type_validator or TypeValidator()
        self.url_validator = url_validator or URLValidator()
        self.duplicate_validator = duplicate_validator or DuplicateValidator()
        self.anomaly_detector = anomaly_detector or AnomalyDetector()
        self.health_scorer = health_scorer or HealthScorer()

    def validate(
        self,
        records: Optional[list[dict[str, Any]]] = None,
        task: Optional[ScrapingTask] = None,
        raw_results: Optional[Any] = None,
        historical_baseline: Optional[HistoricalBaseline] = None,
        extracted_results: Optional[list[dict[str, Any]]] = None,
    ) -> ValidationResult:
        """Perform comprehensive deterministic validation across extracted records and scraping task."""
        actual_records = records if records is not None else (extracted_results or [])
        actual_task = task or ScrapingTask(task_id="unknown", objective="", target_urls=[])
        total_records = len(actual_records)
        fields = actual_task.fields or (list(actual_records[0].keys()) if actual_records else [])

        logger.debug(f"task_id={actual_task.task_id} Validating {total_records} record(s) across {len(fields)} field(s)")

        # 1. Evaluate Field Completeness & Placeholders
        field_metrics: dict[str, FieldMetric] = self.completeness_validator.evaluate_all(actual_records, fields)

        # 2. Evaluate Schema & Types
        schema_metrics: SchemaMetric = self.type_validator.validate_records_schema(
            records=actual_records,
            output_schema=actual_task.output_schema,
            required_fields=actual_task.fields,
        )

        # Update invalid_type_count in field_metrics if schema is present
        if actual_task.output_schema:
            for f, expected_t in actual_task.output_schema.items():
                if f in field_metrics:
                    invalid_types = 0
                    for r in actual_records:
                        v = r.get(f)
                        if v is not None and not self.type_validator.validate_value(v, str(expected_t)):
                            invalid_types += 1
                    field_metrics[f].invalid_type_count = invalid_types

        # 3. Evaluate URLs
        url_fields = [
            f for f, t in (actual_task.output_schema or {}).items()
            if str(t).lower() in ("url", "link", "uri")
        ]
        url_metrics: UrlMetric = self.url_validator.evaluate_urls(actual_records, url_fields=url_fields)

        # 4. Evaluate Duplicates
        duplicate_metrics: DuplicateMetric = self.duplicate_validator.evaluate_duplicates(actual_records)

        # 5. Detect Anomalies & Failures
        anomalies, failures = self.anomaly_detector.detect_anomalies(
            records=actual_records,
            field_metrics=field_metrics,
            duplicate_metrics=duplicate_metrics,
            url_metrics=url_metrics,
            schema_metrics=schema_metrics,
            raw_results=raw_results,
            expected_max_records=actual_task.max_records,
        )

        # 6. Compare with Historical Baseline if available
        if historical_baseline and historical_baseline.run_count > 0:
            temp_result = ValidationResult(
                record_count=total_records,
                field_metrics=field_metrics,
                duplicate_metrics=duplicate_metrics,
            )
            base_anomalies, base_failures = compare_with_baseline(temp_result, historical_baseline)
            anomalies.extend(base_anomalies)
            failures.extend(base_failures)

        # 7. Compute Mathematical Health & Quality Scores
        health_score, quality_score, status = self.health_scorer.calculate_health_score(
            record_count=total_records,
            field_metrics=field_metrics,
            duplicate_metrics=duplicate_metrics,
            url_metrics=url_metrics,
            schema_metrics=schema_metrics,
            expected_max_records=actual_task.max_records,
        )

        # If failures are critical, enforce broken/unstable status
        if any(f.severity == "critical" for f in failures) and status == "healthy":
            status = "broken" if total_records == 0 else "unstable"

        result = ValidationResult(
            status=status,
            health_score=health_score,
            quality_score=quality_score,
            record_count=total_records,
            expected_record_count=actual_task.max_records,
            field_metrics=field_metrics,
            duplicate_metrics=duplicate_metrics,
            url_metrics=url_metrics,
            schema_metrics=schema_metrics,
            anomalies=anomalies,
            failures=failures,
            recommendation=status,
            metadata={
                "task_id": actual_task.task_id,
                "anomalies_count": len(anomalies),
                "failures_count": len(failures),
            },
        )

        logger.debug(
            f"task_id={actual_task.task_id} Validation completed: status={status}, health_score={health_score}, quality_score={quality_score}, anomalies={len(anomalies)}"
        )

        return result
