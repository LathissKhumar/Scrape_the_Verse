"""
Unit & Integration Tests for Twenty CRM Integration in Lead Manager.
"""

from unittest.mock import AsyncMock, patch

import pytest

from MicroServices.Lead_Manager.crm.twenty_adapter import TwentyCRMAdapter
from MicroServices.Lead_Manager.crm.twenty_client import TwentyCRMClient
from MicroServices.Lead_Manager.domain.lead import Lead
from MicroServices.Lead_Manager.domain.opportunity import Opportunity
from MicroServices.Lead_Manager.domain.stage import LeadStage
from MicroServices.Lead_Manager.domain.task import Task, TaskType


@pytest.mark.asyncio
async def test_twenty_client_serialization_and_mock():
    mock_client = TwentyCRMClient(
        base_url="http://mock-twenty:3000", api_key="test_key"
    )

    mock_resp = AsyncMock()
    mock_resp.status_code = 201
    mock_resp.json = lambda: {
        "data": {"id": "comp_123", "name": "Apex Roofing Solutions"}
    }
    mock_resp.text = '{"data": {"id": "comp_123"}}'

    mock_http_client = AsyncMock()
    mock_http_client.__aenter__.return_value = mock_http_client
    mock_http_client.post.return_value = mock_resp

    with patch.object(mock_client, "_client", return_value=mock_http_client):
        company = await mock_client.create_company(
            name="Apex Roofing Solutions",
            domain_name="https://apexroofing.example.com",
            address="Dallas, TX",
            industry="Roofing Services",
        )
        assert company["id"] == "comp_123"
        assert mock_http_client.post.called

    mock_person_resp = AsyncMock()
    mock_person_resp.status_code = 201
    mock_person_resp.json = lambda: {"data": {"id": "person_456"}}
    mock_person_resp.text = '{"data": {"id": "person_456"}}'

    mock_http_client.post.return_value = mock_person_resp
    with patch.object(mock_client, "_client", return_value=mock_http_client):
        person = await mock_client.create_person(
            first_name="Lathiss",
            last_name="Kumar",
            email="lathiss@apexroofing.com",
            phone="+917395895433",
            company_id="comp_123",
        )
        assert person["id"] == "person_456"


@pytest.mark.asyncio
async def test_twenty_adapter_sync_flow():
    mock_client = TwentyCRMClient(base_url="http://mock-twenty:3000")
    mock_client.create_company = AsyncMock(return_value={"id": "comp_abc"})
    mock_client.create_person = AsyncMock(return_value={"id": "person_xyz"})
    mock_client.create_opportunity = AsyncMock(return_value={"id": "opp_789"})
    mock_client.create_note = AsyncMock(return_value={"id": "note_101"})
    mock_client.create_task = AsyncMock(return_value={"id": "task_202"})

    adapter = TwentyCRMAdapter(client=mock_client)
    adapter.enabled = True

    # 1. Test sync_lead
    lead = Lead(
        id="lead_test_001",
        company_name="Apex Roofing Solutions",
        website_url="https://apexroofing.example.com",
        primary_contact_name="Lathiss Kumar",
        primary_contact_email="lathiss@apexroofing.com",
        primary_contact_phone="+917395895433",
        location="Dallas, TX",
        industry="Roofing",
        stage=LeadStage.CONTACTED,
    )
    sync_res = await adapter.sync_lead(lead)
    assert sync_res["synced"] is True
    assert sync_res["twenty_company_id"] == "comp_abc"
    assert sync_res["twenty_person_id"] == "person_xyz"

    # 2. Test sync_opportunities
    opps = [
        Opportunity(
            lead_id=lead.id,
            type="WEBSITE_REDESIGN",
            score=90.0,
            problem_summary="Missing responsive mobile site.",
        ),
        Opportunity(
            lead_id=lead.id,
            type="LOCAL_SEO",
            score=85.0,
            problem_summary="No Google Maps 3-pack listing.",
        ),
    ]
    opp_results = await adapter.sync_opportunities(
        lead_id=lead.id,
        company_name=lead.company_name,
        stage=lead.stage,
        opportunities=opps,
    )
    assert len(opp_results) == 2

    # 3. Test sync_call_notes (Voice Agent call transcript)
    transcript = [
        {"speaker": "agent", "text": "Hi Lathiss, this is Sarah from AgencyOS."},
        {"speaker": "prospect", "text": "Yes, we are looking for a mobile website."},
        {
            "speaker": "agent",
            "text": "Awesome, let's schedule a demo Thursday at 2 PM.",
        },
    ]
    note_res = await adapter.sync_call_notes(
        lead_id=lead.id,
        company_name=lead.company_name,
        transcript=transcript,
        summary="Spoke with Lathiss. Booked discovery demo for Thursday.",
        disposition="MEETING_BOOKED",
        interest_score=95.0,
    )
    assert note_res["id"] == "note_101"
    assert mock_client.create_note.called
    call_args = mock_client.create_note.call_args[1]
    assert "Voice Telephony Summary" in call_args["body"]
    assert "Full Conversation Transcript" in call_args["body"]

    # 4. Test sync_task
    task = Task(
        lead_id=lead.id,
        title="Prepare discovery demo for Apex Roofing",
        type=TaskType.SCHEDULE_MEETING,
    )
    task_res = await adapter.sync_task(lead_id=lead.id, task=task)
    assert task_res["id"] == "task_202"


@pytest.mark.asyncio
async def test_twenty_adapter_graceful_offline_fallback():
    mock_client = TwentyCRMClient(base_url="http://unreachable-twenty:3000")
    # Simulate connection refusal / error
    mock_client.create_company = AsyncMock(
        return_value={"success": False, "error": "Connection refused"}
    )
    mock_client.create_person = AsyncMock(
        return_value={"success": False, "error": "Connection refused"}
    )

    adapter = TwentyCRMAdapter(client=mock_client)
    adapter.enabled = True

    lead = Lead(
        id="lead_test_offline",
        company_name="Offline Corp",
    )
    # Should not raise exception
    sync_res = await adapter.sync_lead(lead)
    assert sync_res["synced"] is True
    assert sync_res["twenty_company_id"] is None


@pytest.mark.asyncio
async def test_twenty_lifecycle_manager():
    from MicroServices.Lead_Manager.crm.lifecycle import TwentyLifecycleManager

    mgr = TwentyLifecycleManager(
        base_url="http://mock-twenty:3000", idle_timeout_seconds=0.1
    )

    with (
        patch.object(
            mgr, "is_crm_responsive", AsyncMock(side_effect=[False, True, True, True])
        ),
        patch("asyncio.create_subprocess_exec") as mock_exec,
    ):
        mock_proc = AsyncMock()
        mock_proc.communicate.return_value = (b"ok", b"")
        mock_proc.returncode = 0
        mock_exec.return_value = mock_proc

        # Test spin_up
        res = await mgr.spin_up(max_wait_seconds=5)
        assert res is True
        assert mock_exec.called

        # Test lease context manager
        async with mgr.lease(auto_spin_down_delay=0.05):
            assert mgr._active_leases == 1

        assert mgr._active_leases == 0

        # Test spin_down
        down_res = await mgr.spin_down(force=True)
        assert down_res is True
