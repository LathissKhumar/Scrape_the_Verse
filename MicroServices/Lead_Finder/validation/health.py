from leadfinder.validation.schemas import (
    DuplicateMetric,
    FieldMetric,
    SchemaMetric,
    UrlMetric,
    ValidationStatus,
)

# Configurable Weights for Health Score
DEFAULT_HEALTH_WEIGHTS = {
    "schema_validity": 0.20,
    "field_completeness": 0.20,
    "record_count_health": 0.15,
    "type_validity": 0.10,
    "url_validity": 0.10,
    "duplicate_health": 0.10,
    "extraction_consistency": 0.15,
}

# Configurable Thresholds for Health Categorization
HEALTHY_THRESHOLD = 0.85
DEGRADED_THRESHOLD = 0.65
UNSTABLE_THRESHOLD = 0.40


class HealthScorer:
    """Computes deterministic health score and quality score based on standardized weighted dimensions."""

    def __init__(self, weights: dict[str, float] | None = None):
        self.weights = weights or DEFAULT_HEALTH_WEIGHTS

    def calculate_health_score(
        self,
        record_count: int,
        field_metrics: dict[str, FieldMetric],
        duplicate_metrics: DuplicateMetric,
        url_metrics: UrlMetric,
        schema_metrics: SchemaMetric,
        expected_max_records: int | None = None,
    ) -> tuple[float, float, ValidationStatus]:
        """Calculate health_score, quality_score, and validation status."""
        if record_count == 0:
            return 0.0, 0.0, "broken"

        # 1. Schema validity dimension (0.0 to 1.0)
        s_schema = schema_metrics.valid_rate

        # 2. Field completeness dimension (average coverage across requested fields)
        coverages = [m.coverage for m in field_metrics.values()]
        s_completeness = sum(coverages) / len(coverages) if coverages else 1.0

        # 3. Record count health dimension
        if expected_max_records and expected_max_records > 0:
            # Ratio of extracted to expected up to 1.0
            ratio = record_count / expected_max_records
            s_count = min(1.0, max(0.2, min(ratio, 1.0)))
        else:
            s_count = 1.0 if record_count >= 1 else 0.0

        # 4. Type validity dimension (fraction of records without invalid type count)
        type_failures = sum(m.invalid_type_count for m in field_metrics.values())
        s_type = max(
            0.0, 1.0 - (type_failures / (record_count * max(1, len(field_metrics))))
        )

        # 5. URL validity dimension
        s_url = url_metrics.valid_rate

        # 6. Duplicate health dimension
        s_dup = max(0.0, 1.0 - duplicate_metrics.duplicate_rate)

        # 7. Extraction consistency dimension (penalty if placeholder count is high or single field collapse)
        min_cov = min(coverages) if coverages else 1.0
        total_placeholders = sum(m.placeholder_count for m in field_metrics.values())
        placeholder_ratio = total_placeholders / (
            record_count * max(1, len(field_metrics))
        )
        s_consistency = max(
            0.0, (min_cov * 0.7) + ((1.0 - min(1.0, placeholder_ratio)) * 0.3)
        )

        # Weighted Health Score sum
        w = self.weights
        health_score = (
            w["schema_validity"] * s_schema
            + w["field_completeness"] * s_completeness
            + w["record_count_health"] * s_count
            + w["type_validity"] * s_type
            + w["url_validity"] * s_url
            + w["duplicate_health"] * s_dup
            + w["extraction_consistency"] * s_consistency
        )

        # Quality Score reflects intrinsic data completeness and validity
        quality_score = (
            0.40 * s_completeness + 0.30 * s_type + 0.15 * s_url + 0.15 * s_dup
        )

        health_score = round(max(0.0, min(1.0, health_score)), 4)
        quality_score = round(max(0.0, min(1.0, quality_score)), 4)

        # Categorize status
        if health_score >= HEALTHY_THRESHOLD:
            status: ValidationStatus = "healthy"
        elif health_score >= DEGRADED_THRESHOLD:
            status = "degraded"
        elif health_score >= UNSTABLE_THRESHOLD:
            status = "unstable"
        else:
            status = "broken"

        return health_score, quality_score, status
