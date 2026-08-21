"""Scorer for computing quantitative repair confidence scores and assigning confidence tiers."""

from app.config.logging import get_logger
from app.config.settings import get_settings
from app.healing.schemas import RepairConfidenceLevel

logger = get_logger("REPAIR_CONFIDENCE_SCORER")

_DEFAULT_HIGH_CONFIDENCE_THRESHOLD = 0.85
_DEFAULT_MEDIUM_CONFIDENCE_THRESHOLD = 0.65


class RepairConfidenceScorer:
    """Computes explainable, multi-signal confidence scores for repair evaluations."""

    def __init__(self) -> None:
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
        weight_candidate = 0.20
        weight_improvement = 0.25
        weight_schema = 0.20
        weight_multi_page = 0.15
        weight_history = 0.10
        weight_attempt_penalty = 0.10

        # Normalized health improvement signal (bounded [0, 1])
        norm_improvement = min(1.0, max(0.0, final_health))

        # Attempt penalty (penalty grows on subsequent attempts)
        attempt_penalty = min(1.0, (attempt_number - 1) * 0.4)

        raw_score = (
            (weight_candidate * candidate_confidence)
            + (weight_improvement * norm_improvement)
            + (weight_schema * schema_valid_rate)
            + (weight_multi_page * multi_page_score)
            + (weight_history * historical_success_rate)
            - (weight_attempt_penalty * attempt_penalty)
        )

        score = round(max(0.0, min(1.0, raw_score)), 3)

        high_threshold = getattr(self.settings, "HIGH_CONFIDENCE_THRESHOLD", _DEFAULT_HIGH_CONFIDENCE_THRESHOLD)
        medium_threshold = getattr(self.settings, "MEDIUM_CONFIDENCE_THRESHOLD", _DEFAULT_MEDIUM_CONFIDENCE_THRESHOLD)

        if score >= high_threshold:
            tier = RepairConfidenceLevel.HIGH
        elif score >= medium_threshold:
            tier = RepairConfidenceLevel.MEDIUM
        else:
            tier = RepairConfidenceLevel.LOW

        logger.debug(f"Calculated repair confidence: score={score:.3f} -> tier={tier.value}")
        return score, tier

