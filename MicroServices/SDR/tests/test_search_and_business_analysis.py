"""
Tests for Layer 3: Search Client, CTA Detector, and Business Analyzer.
"""

import pytest
import sniffio
from MicroServices.SDR.business_analyzer import BusinessAnalyzer
from MicroServices.SDR.cta_detector import CTADetector
from MicroServices.SDR.search_client import DuckDuckGoSearchClient


@pytest.fixture(autouse=True)
def set_async_lib():
    token = sniffio.current_async_library_cvar.set("asyncio")
    yield
    sniffio.current_async_library_cvar.reset(token)


@pytest.mark.asyncio
async def test_duckduckgo_search_context():
    context = await DuckDuckGoSearchClient.gather_business_context(
        company_name="Apex Dental Clinic",
        location="Austin TX",
        industry="Dental",
    )
    assert context["company_name"] == "Apex Dental Clinic"
    assert "raw_context_text" in context
    assert len(context["company_mentions"]) >= 1


def test_cta_detector():
    pages = [
        {
            "title": "Home - Apex Dental",
            "h1": ["Welcome to Apex Dental"],
            "h2": ["Our Services"],
            "links": [{"href": "tel:5551234567"}, {"href": "/about"}],
        }
    ]
    signals = CTADetector.analyze_conversion_signals(pages)
    assert signals["has_phone_cta"] is True
    assert "conversion_score" in signals


@pytest.mark.asyncio
async def test_business_analyzer():
    analyzer = BusinessAnalyzer()
    result = await analyzer.analyze_business(
        company_name="Springfield Family Dentistry",
        website_url="https://springfielddental.example.com",
        location="Springfield",
        industry="Healthcare & Medical",
    )
    assert "business_score" in result
    assert "strengths" in result
    assert "weaknesses" in result
    assert len(result["weaknesses"]) >= 1
