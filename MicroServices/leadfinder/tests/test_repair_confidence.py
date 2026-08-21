from leadfinder.healing.confidence import RepairConfidenceScorer
from leadfinder.healing.schemas import RepairConfidenceLevel


def test_confidence_scorer_high_confidence():
    scorer = RepairConfidenceScorer()
    score, tier = scorer.compute_confidence(
        candidate_confidence=0.95,
        health_improvement=0.80,
        final_health=1.00,
        schema_valid_rate=1.00,
        multi_page_score=1.00,
        attempt_number=1,
    )
    assert score >= 0.85
    assert tier == RepairConfidenceLevel.HIGH


def test_confidence_scorer_medium_confidence():
    scorer = RepairConfidenceScorer()
    score, tier = scorer.compute_confidence(
        candidate_confidence=0.75,
        health_improvement=0.30,
        final_health=0.80,
        schema_valid_rate=0.85,
        multi_page_score=0.75,
        attempt_number=2,
    )
    assert 0.65 <= score < 0.85
    assert tier == RepairConfidenceLevel.MEDIUM


def test_confidence_scorer_low_confidence():
    scorer = RepairConfidenceScorer()
    score, tier = scorer.compute_confidence(
        candidate_confidence=0.40,
        health_improvement=0.10,
        final_health=0.50,
        schema_valid_rate=0.60,
        multi_page_score=0.40,
        attempt_number=3,
    )
    assert score < 0.65
    assert tier == RepairConfidenceLevel.LOW
