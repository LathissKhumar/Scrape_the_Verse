from typing import Any, Optional
from app.validation.schemas import (
    DuplicateMetric,
    FailureItem,
    FailureTaxonomy,
    FieldMetric,
    SchemaMetric,
    UrlMetric,
)


class AnomalyDetector:
    """Identifies quality anomalies, structural defects, and failure classifications."""

    def detect_anomalies(
        self,
        records: list[dict[str, Any]],
        field_metrics: dict[str, FieldMetric],
        duplicate_metrics: DuplicateMetric,
        url_metrics: UrlMetric,
        schema_metrics: SchemaMetric,
        raw_results: Optional[Any] = None,
        expected_max_records: Optional[int] = None,
    ) -> tuple[list[str], list[FailureItem]]:
        """Identify anomalies and produce structured failure items for downstream diagnosis."""
        anomalies: list[str] = []
        failures: list[FailureItem] = []

        total_records = len(records)

        # 1. Check for empty records
        if total_records == 0:
            anomalies.append("Zero structured records were extracted.")
            # Check if raw results existed
            raw_has_content = False
            if raw_results:
                if isinstance(raw_results, list) and len(raw_results) > 0:
                    raw_has_content = True
                elif isinstance(raw_results, str) and len(raw_results.strip()) > 0:
                    raw_has_content = True
                elif isinstance(raw_results, dict) and len(raw_results) > 0:
                    raw_has_content = True

            if raw_has_content:
                failures.append(
                    FailureItem(
                        failure_type=FailureTaxonomy.EXTRACTION_DEGRADATION,
                        severity="critical",
                        message="Scraper returned raw page content, but extraction engine produced 0 records.",
                        evidence={"raw_results_present": True, "extracted_count": 0},
                    )
                )
            else:
                failures.append(
                    FailureItem(
                        failure_type=FailureTaxonomy.SCRAPER_OUTPUT_MISSING,
                        severity="critical",
                        message="Scraper returned empty raw content or encountered transport blocking.",
                        evidence={"raw_results_present": False, "extracted_count": 0},
                    )
                )
            return anomalies, failures

        # 2. Check record count anomalies against explicit expectation
        if expected_max_records and expected_max_records >= 20:
            if total_records < max(2, int(expected_max_records * 0.15)):
                anomalies.append(
                    f"Extracted record count ({total_records}) is substantially below requested limit ({expected_max_records})."
                )
                failures.append(
                    FailureItem(
                        failure_type=FailureTaxonomy.LOW_RECORD_COUNT,
                        severity="medium",
                        message=f"Low record yield: extracted {total_records} records against requested {expected_max_records}.",
                        evidence={"extracted_count": total_records, "expected_max": expected_max_records},
                    )
                )

        # 3. Check field coverage collapse
        for field_name, metric in field_metrics.items():
            if metric.coverage < 0.30:
                anomalies.append(f"Critical coverage collapse for field '{field_name}' ({metric.coverage * 100:.1f}%).")
                failures.append(
                    FailureItem(
                        failure_type=FailureTaxonomy.LOW_FIELD_COVERAGE,
                        severity="high",
                        message=f"Field '{field_name}' has low coverage ({metric.coverage * 100:.1f}%).",
                        evidence={"field": field_name, "coverage": metric.coverage},
                    )
                )
            elif metric.coverage < 0.65:
                anomalies.append(f"Moderate coverage drop for field '{field_name}' ({metric.coverage * 100:.1f}%).")

        # 4. Check duplicate explosion
        if duplicate_metrics.duplicate_rate >= 0.30:
            anomalies.append(f"High duplicate rate detected ({duplicate_metrics.duplicate_rate * 100:.1f}%).")
            failures.append(
                FailureItem(
                    failure_type=FailureTaxonomy.HIGH_DUPLICATE_RATE,
                    severity="high" if duplicate_metrics.duplicate_rate > 0.50 else "medium",
                    message=f"Extracted records contain {duplicate_metrics.duplicate_records} duplicates ({duplicate_metrics.duplicate_rate * 100:.1f}%).",
                    evidence={
                        "duplicate_rate": duplicate_metrics.duplicate_rate,
                        "duplicates": duplicate_metrics.duplicate_records,
                    },
                )
            )

        # 5. Check URL validity
        if url_metrics.total_urls > 0 and url_metrics.valid_rate < 0.70:
            anomalies.append(f"High invalid URL rate ({100 - url_metrics.valid_rate * 100:.1f}% invalid).")
            failures.append(
                FailureItem(
                    failure_type=FailureTaxonomy.INVALID_URLS,
                    severity="medium",
                    message=f"Invalid URL rate: {url_metrics.invalid_urls} invalid out of {url_metrics.total_urls}.",
                    evidence={"valid_rate": url_metrics.valid_rate, "invalid_count": url_metrics.invalid_urls},
                )
            )

        # 6. Check Schema Mismatch
        if schema_metrics.missing_required_fields:
            missing_str = ", ".join(schema_metrics.missing_required_fields)
            anomalies.append(f"Missing required schema fields: {missing_str}")
            failures.append(
                FailureItem(
                    failure_type=FailureTaxonomy.SCHEMA_MISMATCH,
                    severity="critical",
                    message=f"Extraction completely missed required fields: {missing_str}",
                    evidence={"missing_fields": schema_metrics.missing_required_fields},
                )
            )

        return anomalies, failures
