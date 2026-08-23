"""
Unit tests for SDR Opportunity Builder.
"""

from MicroServices.SDR.opportunity_builder import OpportunityBuilder


def test_build_opportunities_from_poor_scores():
    audit_state = {
        "url": "https://example-restaurant.com",
        "scores": {
            "technical": 60.0,
            "onpage": 55.0,
            "content": 50.0,
            "performance": 45.0,
            "schema": 30.0,
            "local": 40.0,
        },
        "issues": ["Missing viewport tag", "Missing Schema.org markup", "High TTFB"],
    }

    opps = OpportunityBuilder.build_opportunities_from_audit(audit_state)
    assert len(opps) >= 3

    opp_types = [o["type"] for o in opps]
    assert "WEBSITE_REDESIGN" in opp_types
    assert "LOCAL_SEO" in opp_types
    assert "SPEED_PERFORMANCE" in opp_types

    # Verify score ranges
    for opp in opps:
        assert 0.0 <= opp["score"] <= 100.0
        assert opp["problem_summary"] is not None
        assert opp["status"] == "IDENTIFIED"


def test_build_opportunities_from_perfect_scores():
    audit_state = {
        "url": "https://perfect-site.com",
        "scores": {
            "technical": 98.0,
            "onpage": 95.0,
            "content": 92.0,
            "performance": 96.0,
            "schema": 90.0,
            "local": 90.0,
        },
        "issues": [],
    }

    opps = OpportunityBuilder.build_opportunities_from_audit(audit_state)
    assert len(opps) >= 1
    assert any(o["type"] in ("CONVERSION_OPTIMIZATION", "WEBSITE_REDESIGN") for o in opps)
