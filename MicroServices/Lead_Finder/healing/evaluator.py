"""Deterministic validation evaluator comparing before/after validation metrics and enforcing regression guards."""

from typing import Any

from leadfinder.config.logging import get_logger
from leadfinder.diagnosis.schemas import DiagnosisResult
from leadfinder.healing.confidence import RepairConfidenceScorer
from leadfinder.healing.schemas import (
    PerformanceSnapshot,
    RepairEvaluation,
    RepairPlan,
)
from leadfinder.validation.schemas import ValidationResult

logger = get_logger("HEALING_EVALUATOR")


class RepairEvaluator:
    """Deterministic validation evaluator comparing before/after validation metrics and enforcing regression guards."""

    def __init__(
        self,
        min_healthy_threshold: float = 0.80,
        min_health_improvement: float = 0.10,
        max_regression_drop: float = 0.05,
        confidence_scorer: RepairConfidenceScorer | None = None,
    ) -> None:
        self.min_healthy_threshold = min_healthy_threshold
        self.min_health_improvement = min_health_improvement
        self.max_regression_drop = max_regression_drop
        self.confidence_scorer = confidence_scorer or RepairConfidenceScorer()

    def snapshot(
        self, val: ValidationResult, strategy: str = "unknown"
    ) -> PerformanceSnapshot:
        """Construct a quantitative performance snapshot from a ValidationResult."""
        field_cov = {k: v.coverage for k, v in val.field_metrics.items()}
        rec_count = val.record_count or (
            val.duplicate_metrics.total_records if val.duplicate_metrics else 0
        )

        return PerformanceSnapshot(
            health=val.health_score,
            quality=val.quality_score,
            records=rec_count,
            field_coverage=field_cov,
            duplicate_rate=val.duplicate_metrics.duplicate_rate
            if val.duplicate_metrics
            else 0.0,
            schema_valid_rate=val.schema_metrics.valid_rate
            if val.schema_metrics
            else 1.0,
            strategy_used=strategy,
        )

    def evaluate(
        self,
        before: ValidationResult,
        after: ValidationResult,
        diagnosis: DiagnosisResult | None = None,
        plan: RepairPlan | None = None,
        strategy_used: str = "unknown",
        multi_page_score: float = 1.0,
        multi_page_results: list[dict[str, Any]] | None = None,
        attempt_number: int = 1,
        target_fields: list[str] | None = None,
    ) -> RepairEvaluation:
        """Deterministically assess whether a candidate repair should be accepted or rejected."""
        repair_id = plan.repair_id if plan else "unspecified"
        before_snap = self.snapshot(before, strategy=strategy_used)
        after_snap = self.snapshot(after, strategy=strategy_used)

        delta_health = after.health_score - before.health_score
        logger.debug(
            f"Evaluating repair_id={repair_id}: before_health={before.health_score:.2f}, "
            f"after_health={after.health_score:.2f} (delta={delta_health:+.2f})"
        )

        regression_detected = False
        rejection_reason: str | None = None

        # 1. Per-field regression check (previously healthy target fields must not degrade)
        valid_target_names = set(target_fields or []) if target_fields else set()
        for field_name, before_cov in before_snap.field_coverage.items():
            # If target fields specified, ignore unrequested internal auxiliary fields (e.g. raw 'title' vs 'product_name')
            if valid_target_names and field_name not in valid_target_names:
                continue
            if before_cov >= 0.80:
                after_cov = after_snap.field_coverage.get(field_name, 0.0)
                if after_cov < (before_cov - self.max_regression_drop):
                    regression_detected = True
                    rejection_reason = (
                        f"Regression detected in field '{field_name}': "
                        f"coverage dropped from {before_cov:.2f} to {after_cov:.2f}"
                    )
                    break

        # 2. Duplicate rate explosion check
        if not regression_detected:
            if after_snap.duplicate_rate > 0.30 and after_snap.duplicate_rate > (
                before_snap.duplicate_rate + 0.15
            ):
                regression_detected = True
                rejection_reason = (
                    f"Duplicate rate explosion: rate increased from "
                    f"{before_snap.duplicate_rate:.2f} to {after_snap.duplicate_rate:.2f}"
                )

        # 3. Schema validity collapse check
        if not regression_detected:
            if after_snap.schema_valid_rate < 0.70 and after_snap.schema_valid_rate < (
                before_snap.schema_valid_rate - 0.15
            ):
                regression_detected = True
                rejection_reason = (
                    f"Schema validity degraded: valid rate dropped from "
                    f"{before_snap.schema_valid_rate:.2f} to {after_snap.schema_valid_rate:.2f}"
                )

        # 4. Critical failure resolution check
        critical_failure_resolved = False
        before_critical = [f for f in before.failures if f.severity == "critical"]
        after_critical = [f for f in after.failures if f.severity == "critical"]
        if (
            before_critical
            and not after_critical
            or (
                not before_critical
                and not after_critical
                and after.health_score >= self.min_healthy_threshold
            )
        ):
            critical_failure_resolved = True

        # 5. Final acceptance decision
        accepted = False
        if regression_detected:
            accepted = False
            logger.warning(f"Repair rejected due to regression: {rejection_reason}")
        else:
            # Condition A: Reached healthy threshold and either resolved critical failure or improved health
            if (
                after.health_score >= self.min_healthy_threshold
                and (critical_failure_resolved or delta_health >= -0.01)
                or delta_health >= self.min_health_improvement
            ):
                accepted = True
            else:
                accepted = False
                rejection_reason = (
                    f"Insufficient health improvement: delta={delta_health:.2f}, "
                    f"after_health={after.health_score:.2f} (required delta>={self.min_health_improvement} "
                    f"or after_health>={self.min_healthy_threshold})"
                )
                logger.debug(f"Repair rejected: {rejection_reason}")

        # Compute confidence score & tier
        cand_conf = plan.confidence if plan else 0.80
        conf_score, conf_tier = self.confidence_scorer.compute_confidence(
            candidate_confidence=cand_conf,
            health_improvement=max(0.0, delta_health),
            final_health=after.health_score,
            schema_valid_rate=after_snap.schema_valid_rate,
            multi_page_score=multi_page_score,
            attempt_number=attempt_number,
        )

        return RepairEvaluation(
            repair_id=repair_id,
            before=before_snap,
            after=after_snap,
            improvement=delta_health,
            critical_failure_resolved=critical_failure_resolved,
            regression_detected=regression_detected,
            accepted=accepted,
            rejection_reason=rejection_reason,
            confidence_score=conf_score,
            confidence_level=conf_tier,
            multi_page_evaluated=bool(multi_page_results),
            multi_page_results=multi_page_results or [],
        )
