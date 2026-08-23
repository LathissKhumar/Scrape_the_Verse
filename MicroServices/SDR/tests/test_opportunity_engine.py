"""
Tests for Opportunity Engine (Layer 5) & Dynamic Service Catalog Matching.
"""

import pytest
from MicroServices.SDR.opportunity_engine import OpportunityEngine, SelectedOffer


def test_evaluate_opportunities_with_website_weaknesses():
    seo_data = {
        "scores": {
            "technical": 65.0,
            "performance": 50.0,
            "schema": 40.0,
            "local": 55.0,
            "conversion": 45.0,
        },
        "issues": ["Missing LocalBusiness Schema", "Large uncompressed images"],
        "conversion_signals": {"has_booking_engine": False, "has_live_chat": False},
    }
    business_data = {
        "business_score": 60.0,
        "weaknesses": ["Slow response times", "No after-hours lead capture"],
    }

    offers = OpportunityEngine.evaluate_opportunities(
        seo_data=seo_data,
        business_data=business_data,
        has_website=True,
    )

    assert len(offers) >= 3
    service_codes = [o.service_code for o in offers]
    assert "WEBSITE_REDESIGN" in service_codes
    assert "LOCAL_SEO" in service_codes
    assert "SPEED_PERFORMANCE" in service_codes

    # Ensure prioritized descending
    assert offers[0].priority_score >= offers[-1].priority_score
    assert offers[0].estimated_price_usd > 0


def test_evaluate_opportunities_for_lead_without_website():
    seo_data = {"scores": {}, "issues": ["No website"]}
    business_data = {"business_score": 50.0, "weaknesses": ["No digital presence"]}

    offers = OpportunityEngine.evaluate_opportunities(
        seo_data=seo_data,
        business_data=business_data,
        has_website=False,
    )

    assert len(offers) == 1
    assert offers[0].service_code == "WEBSITE_REDESIGN"
    assert "Complete Digital Presence" in offers[0].service_title
    assert offers[0].priority_score >= 90.0
