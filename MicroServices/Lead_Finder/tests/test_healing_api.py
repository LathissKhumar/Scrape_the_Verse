from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient
from leadfinder.main import app
from leadfinder.models.schemas import ScrapingResult


@pytest.mark.asyncio
async def test_root_endpoint_reports_phase_5():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["phase"] == 5
        assert data["service"] == "self-healing-scraper"


@pytest.mark.asyncio
async def test_scrape_endpoint_returns_self_healed_metadata():
    transport = ASGITransport(app=app)

    # Mock workflow response
    mock_result = ScrapingResult(
        task_id="test_api_task",
        status="success",
        records=[{"title": "Laptop", "price": "$1000"}],
        metadata={
            "task_id": "test_api_task",
            "record_count": 1,
            "scraper_provider": "local",
            "self_healed": True,
            "repair_attempts": 1,
            "health_before": 0.32,
            "health_after": 0.95,
            "repair_type": "REPAIR_CSS_SELECTORS",
            "repair_history": [
                {
                    "attempt": 1,
                    "repair_type": "REPAIR_CSS_SELECTORS",
                    "health_before": 0.32,
                    "health_after": 0.95,
                    "accepted": True,
                }
            ],
        },
    )

    with patch(
        "leadfinder.main.workflow.ainvoke", new_callable=AsyncMock
    ) as mock_invoke:
        mock_invoke.return_value = {"final_output": mock_result}

        async with AsyncClient(transport=transport, base_url="http://test") as client:
            payload = {
                "query": "Scrape laptops from https://example.com/laptops",
                "target_urls": ["https://example.com/laptops"],
            }
            resp = await client.post("/scrape", json=payload)
            assert resp.status_code == 200
            data = resp.json()

            assert data["status"] == "success"
            assert data["metadata"]["self_healed"] is True
            assert data["metadata"]["repair_type"] == "REPAIR_CSS_SELECTORS"
            assert data["metadata"]["health_after"] == 0.95
            assert data["metadata"]["scraper_provider"] == "local"
            assert len(data["records"]) == 1


@pytest.mark.asyncio
async def test_scrape_endpoint_returns_escalated_metadata():
    transport = ASGITransport(app=app)

    mock_result = ScrapingResult(
        task_id="test_api_task_esc",
        status="failed",
        records=[],
        metadata={
            "task_id": "test_api_task_esc",
            "record_count": 0,
            "self_healed": False,
            "escalated": True,
            "repair_attempts": 3,
            "health_before": 0.30,
            "health_after": 0.35,
        },
        error="Unable to recover scraper after bounded repair attempts",
    )

    with patch(
        "leadfinder.main.workflow.ainvoke", new_callable=AsyncMock
    ) as mock_invoke:
        mock_invoke.return_value = {"final_output": mock_result}

        async with AsyncClient(transport=transport, base_url="http://test") as client:
            payload = {
                "query": "Scrape laptops from https://example.com/laptops",
                "target_urls": ["https://example.com/laptops"],
            }
            resp = await client.post("/scrape", json=payload)
            assert resp.status_code == 200
            data = resp.json()

            assert data["status"] == "failed"
            assert data["metadata"]["self_healed"] is False
            assert data["metadata"]["escalated"] is True
            assert data["metadata"]["repair_attempts"] == 3
