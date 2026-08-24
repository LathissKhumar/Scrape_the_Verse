"""
Unit tests for Agent-to-Agent (A2A) protocol in Lead Manager.
"""

import os

import pytest
from httpx import ASGITransport, AsyncClient

from MicroServices.Lead_Manager.domain.stage import LeadStage
from MicroServices.Lead_Manager.main import app
from MicroServices.Lead_Manager.repository.database import get_db_manager

TEST_DB = ".test_a2a.sqlite"


@pytest.fixture(autouse=True)
async def setup_db():
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    manager = get_db_manager(db_path=TEST_DB)
    await manager.init_db()
    yield manager
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


@pytest.mark.asyncio
async def test_a2a_agent_card_and_invoke():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # 1. Fetch Agent Card
        res_card = await client.get("/.well-known/agent.json")
        assert res_card.status_code == 200
        card = res_card.json()
        assert card["name"] == "LeadManagerAgent"
        assert card["protocol"] == "A2A/1.0"
        capabilities = [c["name"] for c in card["capabilities"]]
        assert "create_lead" in capabilities
        assert "ingest_event" in capabilities
        assert "get_lead_status" in capabilities

        # 2. Invoke create_lead via A2A
        invoke_create = {
            "skill": "create_lead",
            "caller_agent": "LeadFinderAgent",
            "parameters": {
                "company_name": "Horizon Logistics",
                "website_url": "https://horizonlogistics.example.com",
                "primary_contact_email": "ops@horizonlogistics.example.com",
            },
        }
        res_create = await client.post("/a2a/invoke", json=invoke_create)
        assert res_create.status_code == 200
        result = res_create.json()["result"]
        lead_id = result["id"]
        assert result["stage"] == LeadStage.DISCOVERED.value

        # 3. Invoke get_lead_status via A2A
        invoke_status = {
            "skill": "get_lead_status",
            "caller_agent": "DashboardAgent",
            "parameters": {"lead_id": lead_id},
        }
        res_status = await client.post("/a2a/invoke", json=invoke_status)
        assert res_status.status_code == 200
        status_result = res_status.json()["result"]
        assert status_result["company_name"] == "Horizon Logistics"
