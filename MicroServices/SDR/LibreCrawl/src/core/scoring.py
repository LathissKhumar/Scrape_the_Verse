"""
Transparent Scoring, Severity & Business Prioritization Engine (Phases 26-34)
Provides:
- 3-Layer Findings: Observation -> Implication -> Recommendation
- Confidence Model: high, medium, low
- Rule Types: required, recommended, optional (optional items never penalize score)
- Transparent Weighted Scoring Model with configurable weights
- Business Priority Engine: Priority = (Impact × Confidence × PageValue) / Effort
"""

from typing import Any

DEFAULT_CATEGORY_WEIGHTS = {
    "Technical SEO": 0.25,
    "On-Page SEO": 0.20,
    "Content Quality": 0.15,
    "Performance": 0.15,
    "Structured Data": 0.10,
    "Internal Linking": 0.10,
    "Local SEO": 0.05,
}


def create_3layer_finding(
    rule_id: str,
    category: str,
    title: str,
    observation: str,
    implication: str,
    recommendation: str,
    severity: str = "medium",
    confidence: str = "high",
    rule_type: str = "recommended",
    impact: int = 5,
    effort: str = "medium",
    affected_urls: list[str] | None = None,
    evidence: dict[str, Any] | None = None,
    root_cause_id: str | None = None,
) -> dict[str, Any]:
    """
    Constructs a structured 3-layer audit finding.
    """
    sev_upper = severity.upper()
    if sev_upper not in ("CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"):
        sev_upper = "MEDIUM"

    conf_lower = confidence.lower()
    if conf_lower not in ("high", "medium", "low"):
        conf_lower = "medium"

    return {
        "id": f"iss_{rule_id}",
        "rule_id": rule_id,
        "category": category,
        "title": title,
        "severity": sev_upper,
        "confidence": conf_lower,
        "rule_type": rule_type,  # required, recommended, optional
        "observation": observation,
        "implication": implication,
        "recommendation": recommendation,
        "impact_score": impact,
        "estimated_effort": effort,
        "affected_count": len(affected_urls or []),
        "affected_urls": affected_urls or [],
        "evidence": evidence or {},
        "root_cause_id": root_cause_id,
    }


def calculate_transparent_score(
    category_scores: dict[str, float], weights: dict[str, float] | None = None
) -> dict[str, Any]:
    """
    Calculates overall health score using transparent, explainable weights.
    Does NOT allow optional opportunities to falsely tank scores.
    """
    weights = weights or DEFAULT_CATEGORY_WEIGHTS

    total_weight = sum(weights.values()) or 1.0
    weighted_sum = 0.0

    breakdown = {}
    for cat, weight in weights.items():
        score = float(category_scores.get(cat, 100.0))
        normalized_weight = weight / total_weight
        contribution = score * normalized_weight
        weighted_sum += contribution
        breakdown[cat] = {
            "score": round(score, 1),
            "weight": round(normalized_weight, 2),
            "contribution": round(contribution, 1),
        }

    overall_score = round(max(0.0, min(100.0, weighted_sum)), 1)

    return {
        "score": overall_score,
        "weights": weights,
        "breakdown": breakdown,
        "explainable_summary": f"Overall score of {overall_score}/100 computed from weighted category performance.",
    }


def calculate_business_priority(
    finding: dict[str, Any], page_value_multiplier: float = 1.0
) -> float:
    """
    Calculates priority score: (Impact × Confidence × PageValue) / EffortValue
    """
    impact = float(finding.get("impact_score", 5))

    conf_map = {"high": 1.0, "medium": 0.8, "low": 0.5}
    confidence = conf_map.get(str(finding.get("confidence", "medium")).lower(), 0.8)

    effort_map = {"low": 1.0, "medium": 2.0, "high": 3.0}
    effort_val = effort_map.get(
        str(finding.get("estimated_effort", "medium")).lower(), 2.0
    )

    priority_score = (impact * confidence * page_value_multiplier) / effort_val
    return round(priority_score, 2)
