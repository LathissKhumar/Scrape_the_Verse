from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

from leadfinder.agents.scraper import ScraperAgent
from leadfinder.config.settings import Settings
from leadfinder.main import app


def test_scraper_agent_is_brightdata_property():
    """Verify that ScraperAgent correctly exposes the is_brightdata boolean property."""
    mock_client = MagicMock()
    mock_client.is_configured = True
    agent_enabled = ScraperAgent(brightdata_client=mock_client)
    assert agent_enabled.is_brightdata is True

    mock_client.is_configured = False
    agent_disabled = ScraperAgent(brightdata_client=mock_client)
    assert agent_disabled.is_brightdata is False


def test_scrape_smart_routing_gmaps_keyword():
    """Verify POST /scrape automatically routes keyword-only local queries to Google Maps."""
    mock_gmaps = MagicMock()
    mock_gmaps.is_enabled = True
    mock_gmaps.get_local_leads = AsyncMock(
        return_value=[
            {"business_name": "Chennai Plumb Pros", "phone_number": "+91 99999 11111"}
        ]
    )

    with patch("leadfinder.main.gmaps_service", mock_gmaps):
        client = TestClient(app)
        response = client.post(
            "/scrape",
            json={"query": "plumbers in Chennai"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["records"]) == 1
        assert data["records"][0]["business_name"] == "Chennai Plumb Pros"
        assert data["metadata"]["scraper_provider"] == "brightdata_gmaps"


def test_scrape_smart_routing_b2b_keyword():
    """Verify POST /scrape automatically routes keyword-only directory queries to Bright Data B2B."""
    mock_b2b = MagicMock()
    mock_b2b.is_enabled = True
    mock_b2b.generate_leads = AsyncMock(
        return_value=[
            {"company_name": "Tata Solar", "product_title": "Monocrystalline Panel"}
        ]
    )

    # Disable gmaps to ensure B2B fallback is exercised
    mock_gmaps = MagicMock()
    mock_gmaps.is_enabled = False

    with (
        patch("leadfinder.main.brightdata_service", mock_b2b),
        patch("leadfinder.main.gmaps_service", mock_gmaps),
    ):
        client = TestClient(app)
        response = client.post(
            "/scrape",
            json={"query": "solar panels in Delhi"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["records"]) == 1
        assert data["records"][0]["company_name"] == "Tata Solar"
        assert data["metadata"]["scraper_provider"] == "brightdata_b2b"


def test_api_key_auth_enforcement():
    """Verify API authentication enforcement when API_SECRET_KEY is configured."""
    mock_settings = Settings(API_SECRET_KEY="super-secret-key-123")

    with patch("leadfinder.main.settings", mock_settings):
        client = TestClient(app)

        # 1. No key -> 401
        res_no_auth = client.post("/scrape", json={"query": "plumbers in Chennai"})
        assert res_no_auth.status_code == 401
        assert "Invalid or missing API key" in res_no_auth.json()["detail"]

        # 2. Wrong key -> 401
        res_bad_auth = client.post(
            "/scrape",
            json={"query": "plumbers in Chennai"},
            headers={"X-API-Key": "wrong-key"},
        )
        assert res_bad_auth.status_code == 401

        # 3. Valid X-API-Key -> 200
        mock_gmaps = MagicMock()
        mock_gmaps.is_enabled = True
        mock_gmaps.get_local_leads = AsyncMock(
            return_value=[{"business_name": "Test Plumber"}]
        )

        with patch("leadfinder.main.gmaps_service", mock_gmaps):
            res_good_header = client.post(
                "/scrape",
                json={"query": "plumbers in Chennai"},
                headers={"X-API-Key": "super-secret-key-123"},
            )
            assert res_good_header.status_code == 200

            # 4. Valid Authorization: Bearer <key> -> 200
            res_good_bearer = client.post(
                "/scrape",
                json={"query": "plumbers in Chennai"},
                headers={"Authorization": "Bearer super-secret-key-123"},
            )
            assert res_good_bearer.status_code == 200
