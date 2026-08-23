"""
End-to-End Test for the 10-Layer AgencyOS AI SDR Pipeline:
Lead Finder -> Data Normalization -> Parallel Analysis (SEO + Business) ->
Prompt Generation -> Opportunity Engine -> Proposal Generator ->
Outreach Preparation -> Lead Manager CRM -> Voice Agent Qualification & Meeting Booking.
"""

import os
import pytest
import sniffio
from httpx import ASGITransport, AsyncClient
from MicroServices.Lead_Manager.domain.stage import LeadStage
from MicroServices.Lead_Manager.main import app as lead_manager_app
from MicroServices.Lead_Manager.repository.database import get_db_manager
from MicroServices.SDR.orchestrator import SDROrchestrator
from MicroServices.Voice_Agent.domain.call_session import CallDisposition
from MicroServices.Voice_Agent.telephony_adapter import TelephonyAdapter

TEST_E2E_DB = ".test_e2e_pipeline.sqlite"


@pytest.fixture(autouse=True)
def set_async_lib():
    token = sniffio.current_async_library_cvar.set("asyncio")
    yield
    sniffio.current_async_library_cvar.reset(token)


@pytest.fixture(autouse=True)
async def setup_e2e_db():
    if os.path.exists(TEST_E2E_DB):
        os.remove(TEST_E2E_DB)
    manager = get_db_manager(db_path=TEST_E2E_DB)
    await manager.init_db()
    yield manager
    if os.path.exists(TEST_E2E_DB):
        os.remove(TEST_E2E_DB)


@pytest.mark.asyncio
async def test_end_to_end_full_agencyos_sdr_pipeline():
    async with AsyncClient(
        transport=ASGITransport(app=lead_manager_app), base_url="http://test"
    ) as client:
        # 1. Initialize Master SDR Orchestrator
        sdr = SDROrchestrator()

        raw_lead_target = {
            "company_name": "Gouden Draak Bistro & Grill",
            "website": "https://goudendraak.example.com",
            "contact_name": "Li Wei",
            "email": "contact@goudendraak.example.com",
            "phone": "+31 20 1234567",
            "location": "Amsterdam, Netherlands",
            "source": "google_maps_scraper",
        }

        # 2. Run SDR Intelligence Layers (2 through 7)
        sdr_result = await sdr.process_discovered_prospect(
            raw_lead_data=raw_lead_target,
            auto_dispatch_to_lead_manager=False,
        )

        assert sdr_result["success"] is True
        assert sdr_result["has_website"] is True
        assert sdr_result["normalized_lead"]["industry"] == "Hospitality & Dining"
        assert "prompt_pack" in sdr_result
        assert "selected_offers" in sdr_result
        assert len(sdr_result["selected_offers"]) >= 1
        assert "proposal" in sdr_result
        assert "outreach_pack" in sdr_result

        # 3. Ingest into Lead Manager CRM (Layer 8)
        norm = sdr_result["normalized_lead"]
        offers = sdr_result["selected_offers"]
        prop = sdr_result["proposal"]
        outreach = sdr_result["outreach_pack"]

        lead_payload = {
            "company_name": norm["company_name"],
            "industry": norm["industry"],
            "location": norm["location"],
            "website_url": norm["website_url"],
            "primary_contact_name": norm["primary_contact_name"],
            "primary_contact_email": norm["primary_contact_email"],
            "primary_contact_phone": norm["primary_contact_phone"],
            "fit_score": 85.0,
            "opportunity_score": offers[0]["priority_score"],
            "recommended_services": [o["service_title"] for o in offers if o.get("recommended")],
            "metadata": {
                "dedupe_key": norm["dedupe_key"],
                "proposal_id": prop["proposal_id"],
                "email_touches": len(outreach["email_sequence"]),
            },
        }

        res_lead = await client.post("/api/v1/leads", json=lead_payload)
        assert res_lead.status_code == 201
        created_lead = res_lead.json()
        lead_id = created_lead["id"]
        assert created_lead["stage"] == LeadStage.DISCOVERED.value

        # 4. Ingest Opportunities
        opp_events = [
            {
                "type": o["service_code"],
                "score": o["priority_score"],
                "problem_summary": o["problem_addressed"],
                "evidence": [{"deliverables": o["deliverables"]}],
                "recommended": o.get("recommended", True),
            }
            for o in offers
        ]
        res_opp = await client.post(
            "/api/v1/events",
            json={
                "type": "opportunity.created",
                "lead_id": lead_id,
                "actor": "SDROrchestrator",
                "payload": {"opportunities": opp_events},
            },
        )
        assert res_opp.status_code == 200

        # 5. Ingest Proposal Created -> Transition to PROPOSAL_READY
        res_prop = await client.post(
            "/api/v1/events",
            json={
                "type": "proposal.created",
                "lead_id": lead_id,
                "actor": "SDROrchestrator",
                "payload": {
                    "summary": prop["executive_summary"],
                    "proposal_id": prop["proposal_id"],
                    "recommended_services": lead_payload["recommended_services"],
                },
            },
        )
        assert res_prop.status_code == 200
        assert res_prop.json()["new_stage"] == LeadStage.PROPOSAL_READY.value

        # Verify Tasks generated
        res_tasks = await client.get(f"/api/v1/leads/{lead_id}/tasks")
        assert res_tasks.status_code == 200
        tasks = res_tasks.json()
        task_types = [t["type"] for t in tasks]
        assert "REVIEW_PROPOSAL" in task_types

        # 6. Human Approves Proposal -> Advances to CONTACT_READY
        res_approve = await client.post(
            "/api/v1/events",
            json={
                "type": "proposal.approved",
                "lead_id": lead_id,
                "actor": "AccountExec",
                "payload": {"notes": "Approved for omnichannel outreach."},
            },
        )
        assert res_approve.status_code == 200
        assert res_approve.json()["new_stage"] == LeadStage.CONTACT_READY.value

        # 7. Voice Agent Simulation (Layer 9)
        voice_adapter = TelephonyAdapter(lead_manager_url="http://test")
        call_session = await voice_adapter.simulate_call(
            company_name=norm["company_name"],
            contact_name=norm["primary_contact_name"],
            has_website=True,
            simulated_prospect_responses=[
                "Yes, speaking, what is this regarding?",
                "That makes sense, we have been thinking about a redesign.",
                "Thursday afternoon at 2 PM works for a call.",
            ],
        )
        assert call_session.disposition == CallDisposition.MEETING_BOOKED

        # 8. Book Meeting in Lead Manager
        res_meeting = await client.post(
            "/api/v1/meetings",
            json={
                "lead_id": lead_id,
                "title": f"Discovery Call with {norm['company_name']}",
                "scheduled_at": "2026-08-27T14:00:00Z",
                "duration_minutes": 30,
                "organizer_email": "sales@agencyos.local",
                "attendee_email": norm["primary_contact_email"],
                "notes": call_session.call_summary,
            },
        )
        assert res_meeting.status_code in (200, 201)
        meeting_data = res_meeting.json()
        assert meeting_data["title"] == f"Discovery Call with {norm['company_name']}"

        # 9. Verify Final Lead State
        res_final_lead = await client.get(f"/api/v1/leads/{lead_id}")
        assert res_final_lead.status_code == 200
        final_lead = res_final_lead.json()
        assert final_lead["stage"] == LeadStage.MEETING_SCHEDULED.value
        assert len(final_lead["recommended_services"]) >= 1
