import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient

from app.agents.gmaps import GoogleMapsAgent
from app.gmaps.pipeline import GoogleMapsPipeline
from app.gmaps.service import GoogleMapsService
from app.models.schemas import ScrapingRequest, ScrapingResult, ScrapingTask


def test_gmaps_pipeline_url_formatting():
    """Verify Google Maps search URL generation."""
    pipeline = GoogleMapsPipeline()

    url1 = pipeline.format_maps_search_url("plumbers", location="Chennai")
    assert url1 == "https://www.google.com/maps/search/plumbers+in+Chennai"

    url2 = pipeline.format_maps_search_url("electricians in Bangalore")
    assert url2 == "https://www.google.com/maps/search/electricians+in+Bangalore"

    direct_url = "https://www.google.com/maps/search/carpenter"
    assert pipeline.format_maps_search_url(direct_url) == direct_url


def test_gmaps_lead_normalization():
    """Verify normalization of various raw Google Maps records."""
    pipeline = GoogleMapsPipeline()

    raw = {
        "title": "Chennai Express Plumbers",
        "phone": "+91 98401 23456",
        "rating": "4.8 (145)",
        "reviews": "145 reviews",
        "address": "12, GST Road, Guindy, Chennai",
        "website": "https://chennaiexpressplumbers.com",
        "category": "Plumber",
        "url": "https://maps.google.com/?cid=12345",
    }

    normalized = pipeline.normalize_lead(raw)
    assert normalized["business_name"] == "Chennai Express Plumbers"
    assert normalized["phone_number"] == "+91 98401 23456"
    assert normalized["rating"] == 4.8
    assert normalized["reviews_count"] == 145
    assert normalized["address"] == "12, GST Road, Guindy, Chennai"
    assert normalized["website"] == "https://chennaiexpressplumbers.com"
    assert normalized["category"] == "Plumber"
    assert normalized["maps_url"] == "https://maps.google.com/?cid=12345"


def test_gmaps_agent_query_parsing():
    """Verify that GoogleMapsAgent accurately decomposes category and location."""
    agent = GoogleMapsAgent()

    cat1, loc1 = agent.parse_query_and_location("plumbers in Chennai")
    assert cat1.lower() == "plumbers"
    assert loc1.lower() == "chennai"

    cat2, loc2 = agent.parse_query_and_location("solar panel suppliers near Coimbatore")
    assert cat2.lower() == "solar panel suppliers"
    assert loc2.lower() == "coimbatore"

    cat3, loc3 = agent.parse_query_and_location("restaurants")
    assert cat3 == "restaurants"
    assert loc3 is None


@pytest.mark.asyncio
async def test_gmaps_agent_delegation_execution():
    """Verify Agent-to-Agent communication where GoogleMapsAgent receives and executes a delegated task."""
    mock_service = MagicMock(spec=GoogleMapsService)
    mock_service.get_local_leads = AsyncMock(
        return_value=[
            {
                "business_name": "FastFix Plumbing",
                "phone_number": "+91 94440 12345",
                "rating": 4.9,
                "reviews_count": 88,
                "address": "T Nagar, Chennai",
                "category": "Plumber",
                "website": "https://fastfix.in",
            }
        ]
    )

    agent = GoogleMapsAgent(service=mock_service)
    task = ScrapingTask(
        task_id="agent-delegation-001",
        objective="Find plumbers in Chennai",
        target_urls=["https://www.google.com/maps/search/plumbers+in+chennai"],
    )

    result = await agent.execute_agent_delegation(task, source_agent="ScrapingPlannerAgent")

    assert result.status == "success"
    assert result.task_id == "agent-delegation-001"
    assert len(result.records) == 1
    assert result.records[0]["business_name"] == "FastFix Plumbing"
    assert result.metadata["agent"] == "GoogleMapsAgent"
    assert result.metadata["delegated_by"] == "ScrapingPlannerAgent"
    assert result.metadata["category"].lower() == "plumbers"
    assert result.metadata["location"].lower() == "chennai"


def test_api_gmaps_leads_endpoint():
    """Test dedicated POST /api/v1/gmaps/leads endpoint."""
    from app.main import app

    mock_service = MagicMock(spec=GoogleMapsService)
    mock_service.is_enabled = True
    mock_service.get_local_leads = AsyncMock(
        return_value=[
            {
                "business_name": "Apollo Electricals",
                "phone_number": "+91 98400 99999",
                "address": "Velachery, Chennai",
                "rating": 4.7,
            }
        ]
    )

    with patch("app.main.gmaps_service", mock_service):
        client = TestClient(app)
        response = client.post(
            "/api/v1/gmaps/leads",
            json={"query": "electricians in Chennai"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "electricians in Chennai"
        assert data["total_leads"] == 1
        assert data["leads"][0]["business_name"] == "Apollo Electricals"
