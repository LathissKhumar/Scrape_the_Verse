"""
Tests for Voice Agent Microservice (Port 8084).
Covers health checks, A2A agent card, simulated call flows, dynamic intent classification,
2-strike soft-convincing with free PDF audit, and firm exit on second rejection.
"""

import pytest
import sniffio
from httpx import ASGITransport, AsyncClient

from MicroServices.Voice_Agent.domain.call_session import CallDisposition, CallStatus
from MicroServices.Voice_Agent.server import app
from MicroServices.Voice_Agent.state_machine import VoiceConversationEngine
from MicroServices.Voice_Agent.telephony_adapter import TelephonyAdapter


@pytest.fixture(autouse=True)
def set_async_lib():
    token = sniffio.current_async_library_cvar.set("asyncio")
    yield
    sniffio.current_async_library_cvar.reset(token)


@pytest.mark.asyncio
async def test_voice_agent_health_and_card():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        res_health = await client.get("/health")
        assert res_health.status_code == 200
        assert res_health.json()["service"] == "voice_agent"

        res_card = await client.get("/.well-known/agent.json")
        assert res_card.status_code == 200
        card = res_card.json()
        assert card["name"] == "VoiceAgent"
        assert card["protocol"] == "A2A/1.0"


@pytest.mark.asyncio
async def test_simulated_call_flow_meeting_booked():
    adapter = TelephonyAdapter()
    session = await adapter.simulate_call(
        company_name="Apex Dental",
        contact_name="Dr. Smith",
        has_website=False,
        simulated_prospect_responses=[
            "Yes, this is Dr. Smith, go ahead.",
            "That sounds very helpful, how do you handle local SEO?",
            "Thursday at 2 PM works great for me.",
        ],
    )
    assert session.status == CallStatus.COMPLETED
    assert session.disposition == CallDisposition.MEETING_BOOKED
    assert session.interest_score >= 90.0
    assert len(session.transcript) >= 6


@pytest.mark.asyncio
async def test_first_no_offers_free_audit_pdf_and_second_no_exits():
    """Verify that first 'no' gently soft-convinces with free PDF audit, and second 'no' leaves."""
    engine = VoiceConversationEngine(
        company_name="Solomon Legal", contact_name="Solomon", has_website=True
    )
    engine.start_conversation()

    # 1. First 'No' -> Agent offers free 1-page PDF audit
    res1 = await engine.process_turn_async("No, I'm not really interested right now.")
    assert (
        "pdf" in res1["agent_response"].lower()
        or "audit" in res1["agent_response"].lower()
    )
    assert res1["new_state"] == "FAQ_AND_OBJECTIONS"
    assert engine.rejection_count == 1

    # 2. Second 'No' -> Agent politely exits and updates records
    res2 = await engine.process_turn_async("No thanks, please don't email me.")
    assert res2["disposition"] == CallDisposition.NOT_INTERESTED
    assert res2["new_state"] == "CLOSING"
    assert engine.interest_score <= 20.0
    assert (
        "update our records" in res2["agent_response"].lower()
        or "appreciate your time" in res2["agent_response"].lower()
    )


@pytest.mark.asyncio
async def test_first_no_followed_by_agreeing_to_pdf_sends_pdf():
    """Verify that when user agrees to the free audit PDF after initial hesitation, PDF is sent."""
    engine = VoiceConversationEngine(
        company_name="Solomon Legal", contact_name="Solomon", has_website=True
    )
    engine.start_conversation()

    # 1. First 'No'
    await engine.process_turn_async("No, we don't have budget for a redesign.")
    assert engine.rejection_count == 1

    # 2. User agrees to free PDF
    res2 = await engine.process_turn_async("Alright, you can email the free PDF over.")
    assert res2["disposition"] == CallDisposition.REQUESTED_INFO
    assert engine.pdf_audit_sent is True
    assert (
        "pdf" in res2["agent_response"].lower()
        or "audit" in res2["agent_response"].lower()
    )


@pytest.mark.asyncio
async def test_hard_dnc_immediately_exits():
    """Verify that explicit 'stop calling / remove me' immediately exits on turn 1."""
    engine = VoiceConversationEngine(
        company_name="Apex Logistics", contact_name="Bob", has_website=True
    )
    engine.start_conversation()

    res = await engine.process_turn_async(
        "Stop calling me and remove me from your list immediately."
    )
    assert res["disposition"] == CallDisposition.NOT_INTERESTED
    assert res["new_state"] == "CLOSING"
    assert "update our records" in res["agent_response"].lower()


@pytest.mark.asyncio
async def test_pricing_question_handled():
    """Verify that pricing questions are answered directly rather than forcing a meeting."""
    engine = VoiceConversationEngine(
        company_name="Zen Spa", contact_name="Zen", has_website=True
    )
    engine.start_conversation()

    res = await engine.process_turn_async("How much does this service cost?")
    assert res["disposition"] in (
        CallDisposition.INTERESTED,
        CallDisposition.REQUESTED_INFO,
    )
    assert (
        "free" in res["agent_response"].lower()
        or "report" in res["agent_response"].lower()
    )
    assert res["new_state"] in ("FAQ_AND_OBJECTIONS", "PITCH")


@pytest.mark.asyncio
async def test_objection_handled_existing_agency():
    """Verify that 'already have a designer' objection is acknowledged gracefully."""
    engine = VoiceConversationEngine(
        company_name="Urban Cafe", contact_name="Marco", has_website=True
    )
    engine.start_conversation()

    res = await engine.process_turn_async(
        "We already have a web designer working on our site."
    )
    assert res["disposition"] in (
        CallDisposition.REQUESTED_INFO,
        CallDisposition.INTERESTED,
    )
    assert (
        "web team" in res["agent_response"].lower()
        or "report" in res["agent_response"].lower()
    )
    assert res["new_state"] == "FAQ_AND_OBJECTIONS"


@pytest.mark.asyncio
async def test_busy_callback_handled():
    """Verify that 'I'm driving, call me back' sets CALL_BACK_LATER."""
    engine = VoiceConversationEngine(
        company_name="Metro Plumbing", contact_name="Joe", has_website=True
    )
    engine.start_conversation()

    res = await engine.process_turn_async(
        "I am driving in traffic right now, please call back later."
    )
    assert res["disposition"] == CallDisposition.CALL_BACK_LATER
    assert res["new_state"] == "CLOSING"
    assert (
        "better time" in res["agent_response"].lower()
        or "reach back out" in res["agent_response"].lower()
    )


@pytest.mark.asyncio
async def test_voice_agent_api_simulation_endpoint():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        payload = {
            "company_name": "Gouden Draak",
            "has_website": True,
            "simulated_prospect_responses": [
                "Yes, who is this?",
                "That sounds interesting, tell me more.",
                "Friday morning works for a quick call.",
            ],
        }
        res = await client.post("/api/v1/voice/simulate-call", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "COMPLETED"
        assert data["disposition"] == "MEETING_BOOKED"
        assert "transcript" in data
