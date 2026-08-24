"""
API route tests for SDR Microservice (:8081).
"""

import pytest
import sniffio
from httpx import ASGITransport, AsyncClient

from MicroServices.SDR.server import app


@pytest.fixture(autouse=True)
def set_async_lib():
    token = sniffio.current_async_library_cvar.set("asyncio")
    yield
    sniffio.current_async_library_cvar.reset(token)


@pytest.mark.asyncio
async def test_sdr_health_and_ready():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        res_health = await client.get("/health")
        assert res_health.status_code == 200
        assert res_health.json()["service"] == "sdr_service"

        res_ready = await client.get("/ready")
        assert res_ready.status_code == 200
        assert res_ready.json()["status"] == "ready"


@pytest.mark.asyncio
async def test_sdr_agent_card():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        res = await client.get("/.well-known/agent.json")
        assert res.status_code == 200
        card = res.json()
        assert card["name"] == "SDRAgent"
        capabilities = [c["name"] for c in card["capabilities"]]
        assert "audit_website" in capabilities
        assert "execute_full_sdr_pipeline" in capabilities


@pytest.mark.asyncio
async def test_sdr_audit_endpoint():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        payload = {"url": "https://example-bakery.com", "max_pages": 5}
        res = await client.post("/api/v1/audit", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert "overall_seo_score" in data
        assert "scores" in data
        assert "categories" in data
