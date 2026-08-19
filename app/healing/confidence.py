"""Scorer for computing quantitative repair confidence scores and assigning confidence tiers."""

from typing import Optional
from app.config.logging import get_logger
from app.config.settings import get_settings
from app.healing.schemas import RepairConfidenceLevel

logger = get_logger("REPAIR_CONFIDENCE_SCORER")


class RepairConfidenceScorer:
    """Computes explainable, multi-signal confidence scores for repair evaluations."""

    def __init__(self):
        self.settings = get_settings()

    def compute_confidence(
        self,
        candidate_confidence: float = 0.85,
        health_improvement: float = 0.50,
        final_health: float = 1.00,
        schema_valid_rate: float = 1.00,
        multi_page_score: float = 1.00,
        historical_success_rate: float = 0.80,
        attempt_number: int = 1,
    ) -> tuple[float, RepairConfidenceLevel]:
        """Compute composite repair confidence score and determine tier (HIGH, MEDIUM, LOW).

        Returns:
            (confidence_score, confidence_level)
        """
        # 1. Weights
        w_cand = 0.20
        w_imp = 0.25
        w_schema = 0.20
        w_mp = 0.15
        w_hist = 0.10
        w_att_penalty = 0.10

        # Normalized health improvement signal (bounded [0, 1])
        norm_imp = min(1.0, max(0.0, final_health))

        # Attempt penalty (penalty grows on subsequent attempts)
        att_penalty = min(1.0, (attempt_number - 1) * 0.4)

        raw_score = (
            (w_cand * candidate_confidence)
            + (w_imp * norm_imp)
            + (w_schema * schema_valid_rate)
            + (w_mp * multi_page_score)
            + (w_hist * historical_success_rate)
            - (w_att_penalty * att_penalty)
        )

        score = round(max(0.0, min(1.0, raw_score)), 3)

        high_thresh = getattr(self.settings, "HIGH_CONFIDENCE_THRESHOLD", 0.85)
        med_thresh = getattr(self.settings, "MEDIUM_CONFIDENCE_THRESHOLD", 0.65)

        if score >= high_thresh:
            tier = RepairConfidenceLevel.HIGH
        elif score >= med_thresh:
            tier = RepairConfidenceLevel.MEDIUM
        else:
            tier = RepairConfidenceLevel.LOW

        logger.info(f"Calculated repair confidence: score={score:.3f} -> tier={tier.value}")
        return score, tier
