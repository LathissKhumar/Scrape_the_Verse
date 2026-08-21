from typing import Any, Optional
from pydantic import BaseModel, Field
from app.validation.schemas import FailureItem, FailureTaxonomy, ValidationResult


class HistoricalBaseline(BaseModel):
    """In-memory historical reference baseline derived from previous successful scraping runs."""

    average_record_count: float = 0.0
    field_coverage: dict[str, float] = Field(default_factory=dict)
    average_duplicate_rate: float = 0.0
    average_health_score: float = 1.0
    run_count: int = 0


def build_baseline(previous_results: list[ValidationResult]) -> HistoricalBaseline:
    """Construct an aggregated HistoricalBaseline from a list of past ValidationResults."""
    if not previous_results:
        return HistoricalBaseline()

    total_runs = len(previous_results)
    total_records = sum(r.record_count for r in previous_results)
    total_dups = sum(r.duplicate_metrics.duplicate_rate for r in previous_results)
    total_health = sum(r.health_score for r in previous_results)

    # Aggregate field coverage
    all_fields: set[str] = set()
    for r in previous_results:
        all_fields.update(r.field_metrics.keys())

    field_coverage: dict[str, float] = {}
    for f in all_fields:
        coverages = [r.field_metrics[f].coverage for r in previous_results if f in r.field_metrics]
        if coverages:
            field_coverage[f] = round(sum(coverages) / len(coverages), 4)

    return HistoricalBaseline(
        average_record_count=round(total_records / total_runs, 2),
        field_coverage=field_coverage,
        average_duplicate_rate=round(total_dups / total_runs, 4),
        average_health_score=round(total_health / total_runs, 4),
        run_count=total_runs,
    )


def compare_with_baseline(
    current: ValidationResult,
    baseline: HistoricalBaseline,
    count_drop_threshold: float = 0.50,
    coverage_drop_threshold: float = 0.25,
) -> tuple[list[str], list[FailureItem]]:
    """Compare current validation result against historical baseline and flag significant deviations."""
    anomalies: list[str] = []
    failures: list[FailureItem] = []

    if baseline.run_count == 0 or baseline.average_record_count == 0:
        return anomalies, failures

    # 1. Record count drop deviation
    if baseline.average_record_count >= 10:
        drop_pct = (baseline.average_record_count - current.record_count) / baseline.average_record_count
        if drop_pct >= count_drop_threshold:
            anomalies.append(
                f"Significant record count drop: extracted {current.record_count} vs historical average {baseline.average_record_count:.1f} ({drop_pct * 100:.1f}% drop)."
            )
            failures.append(
                FailureItem(
                    failure_type=FailureTaxonomy.EXTRACTION_DEGRADATION,
                    severity="high",
                    message=f"Yield dropped {drop_pct * 100:.1f}% below historical baseline.",
                    evidence={
                        "current_count": current.record_count,
                        "baseline_average": baseline.average_record_count,
                        "drop_ratio": round(drop_pct, 4),
                    },
                )
            )

    # 2. Field coverage drop deviation
    for f, base_cov in baseline.field_coverage.items():
        if f in current.field_metrics:
            curr_cov = current.field_metrics[f].coverage
            cov_drop = base_cov - curr_cov
            if cov_drop >= coverage_drop_threshold:
                anomalies.append(
                    f"Coverage drop for field '{f}': {curr_cov * 100:.1f}% vs historical {base_cov * 100:.1f}%."
                )
                failures.append(
                    FailureItem(
                        failure_type=FailureTaxonomy.LOW_FIELD_COVERAGE,
                        severity="high",
                        message=f"Field '{f}' coverage dropped by {cov_drop * 100:.1f}% compared to baseline.",
                        evidence={
                            "field": f,
                            "current_coverage": curr_cov,
                            "baseline_coverage": base_cov,
                        },
                    )
                )

    return anomalies, failures
