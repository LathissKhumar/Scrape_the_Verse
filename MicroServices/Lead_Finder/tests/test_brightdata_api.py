"""Integration tests for Bright Data FastAPI endpoints."""

from unittest.mock import AsyncMock, patch

import pytest
from leadfinder.main import app
from starlette.testclient import TestClient


@pytest.fixture
def client():
    return TestClient(app)


def test_resolve_scraper_endpoint(client):
    payload = {
        "url": "https://example.com/products",
        "description": "Extract products",
        "fields": [
            {"name": "product_name", "description": "The name"},
            {"name": "price", "description": "The price"},
        ],
    }

    with patch(
        "leadfinder.main.brightdata_service.resolve_scraper", new_callable=AsyncMock
    ) as mock_resolve:
        from leadfinder.brightdata.schemas import ScraperResolveResponse

        mock_resolve.return_value = ScraperResolveResponse(
            action="create",
            status="creating",
            job_id="job_test_001",
            scraper_id="scraper_test_001",
        )

        response = client.post("/scrapers/resolve", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["action"] == "create"
        assert data["job_id"] == "job_test_001"


def test_get_scraper_job_endpoint(client):
    with patch("leadfinder.main.brightdata_service.jobs.get_job") as mock_get_job:
        from leadfinder.brightdata.schemas import CollectorJobRecord, CollectorStatus

        mock_get_job.return_value = CollectorJobRecord(
            job_id="job_test_001",
            scraper_id="scraper_test_001",
            status=CollectorStatus.READY,
            collector_id="c_test_col_123",
            error=None,
        )

        response = client.get("/scrapers/jobs/job_test_001")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        assert data["collector_id"] == "c_test_col_123"


def test_get_scraper_job_not_found(client):
    with patch("leadfinder.main.brightdata_service.jobs.get_job", return_value=None):
        response = client.get("/scrapers/jobs/job_non_existent")
        assert response.status_code == 404


def test_run_scraper_endpoint(client):
    payload = {
        "collector_id": "c_test_col_123",
        "url": "https://example.com/items",
    }

    with patch(
        "leadfinder.main.brightdata_service.run_collector", new_callable=AsyncMock
    ) as mock_run:
        from leadfinder.brightdata.schemas import ScraperRunResponse

        mock_run.return_value = ScraperRunResponse(
            collector_id="c_test_col_123",
            status="success",
            data=[{"item": "Sample"}],
            elapsed_ms=120.5,
        )

        response = client.post("/scrapers/run", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]) == 1


def test_heal_scraper_endpoint(client):
    payload = {
        "collector_id": "c_test_col_123",
        "failure_description": "Selectors broke after update",
    }

    with patch(
        "leadfinder.main.brightdata_service.heal_collector", new_callable=AsyncMock
    ) as mock_heal:
        from leadfinder.brightdata.schemas import ScraperHealResponse

        mock_heal.return_value = ScraperHealResponse(
            collector_id="c_test_col_123",
            status="ready",
            message="Healed",
        )

        response = client.post("/scrapers/heal", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"


def test_list_scrapers_endpoint(client):
    response = client.get("/scrapers")
    assert response.status_code == 200
    data = response.json()
    assert "scrapers" in data
    assert "total" in data
