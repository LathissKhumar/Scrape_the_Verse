"""
Tests for Data Normalization Layer (Layer 2).
"""

import pytest
from MicroServices.SDR.normalizer import DataNormalizer


def test_clean_website_url():
    url1, domain1 = DataNormalizer.clean_website_url("www.goudendraak.nl/menu")
    assert url1 == "https://www.goudendraak.nl/menu"
    assert domain1 == "goudendraak.nl"

    url2, domain2 = DataNormalizer.clean_website_url("http://example-dentist.com")
    assert url2 == "http://example-dentist.com"
    assert domain2 == "example-dentist.com"

    url3, domain3 = DataNormalizer.clean_website_url(None)
    assert url3 is None
    assert domain3 is None


def test_clean_phone_and_email():
    clean_phone = DataNormalizer.clean_phone("(555) 234-5678")
    assert "5552345678" in clean_phone

    valid_email, email_str = DataNormalizer.validate_email("INFO@Company.com ")
    assert valid_email is True
    assert email_str == "info@company.com"

    invalid_email, _ = DataNormalizer.validate_email("not-an-email")
    assert invalid_email is False


def test_classify_industry():
    ind1 = DataNormalizer.classify_industry("Dr. Smith Family Dental Care")
    assert ind1 == "Healthcare & Medical"

    ind2 = DataNormalizer.classify_industry("Apex Roofing and Solar Solutions")
    assert ind2 == "Home Services & Trades"

    ind3 = DataNormalizer.classify_industry("Gouden Draak Bistro")
    assert ind3 == "Hospitality & Dining"


def test_normalize_lead():
    raw_lead = {
        "company_name": "  City Smiles Dental Care  ",
        "website": "www.citysmiles.com",
        "phone": "(123) 456-7890",
        "email": "contact@citysmiles.com",
        "address": "123 Main St, Springfield",
    }
    normalized = DataNormalizer.normalize_lead(raw_lead)
    assert normalized["company_name"] == "City Smiles Dental Care"
    assert normalized["domain"] == "citysmiles.com"
    assert normalized["has_website"] is True
    assert normalized["industry"] == "Healthcare & Medical"
    assert normalized["is_email_valid"] is True
    assert len(normalized["dedupe_key"]) == 16
