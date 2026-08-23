"""
API route tests for Lead Manager.
"""

import os
import pytest
from httpx import ASGITransport, AsyncClient
from MicroServices.Lead_Manager.domain.stage import LeadStage
from MicroServices.Lead_Manager.main import app
from MicroServices.Lead_Manager.repository.database import get_db_manager

TEST_DB = ".test_api.sqlite"


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
async def test_lead_api_lifecycle():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Health check
        res = await client.get("/health")
        assert res.status_code == 200
        assert res.json()["status"] == "healthy"

        # 2. Create Lead
        payload = {
            "company_name": "Nexus Dynamics",
            "industry": "Software Consulting",
            "website_url": "https://nexusdynamics.example.com",
            "primary_contact_name": "Alex Vance",
            "primary_contact_email": "alex@nexusdynamics.example.com",
        }
        res_create = await client.post("/api/v1/leads", json=payload)
        assert res_create.status_code == 201
        lead_data = res_create.json()
        lead_id = lead_data["id"]
        assert lead_data["stage"] == LeadStage.DISCOVERED.value

        # 3. Check Tasks created for DISCOVERED lead
        res_tasks = await client.get(f"/api/v1/leads/{lead_id}/tasks")
        assert res_tasks.status_code == 200
        assert len(res_tasks.json()) >= 1

        # 4. Ingest Event (lead.researched)
        event_payload = {
            "type": "lead.researched",
            "lead_id": lead_id,
            "actor": "SDR",
            "payload": {"notes": "Verified business LinkedIn and company size."},
        }
        res_event = await client.post("/api/v1/events", json=event_payload)
        assert res_event.status_code == 200
        assert res_event.json()["new_stage"] == LeadStage.RESEARCHED.value

        # 5. Fetch updated lead
        res_get = await client.get(f"/api/v1/leads/{lead_id}")
        assert res_get.status_code == 200
        assert res_get.json()["stage"] == LeadStage.RESEARCHED.value

        # 6. Pipeline stats
        res_stats = await client.get("/api/v1/leads/pipeline/stats")
        assert res_stats.status_code == 200
        stats = res_stats.json()
        assert stats.get(LeadStage.RESEARCHED.value) == 1
