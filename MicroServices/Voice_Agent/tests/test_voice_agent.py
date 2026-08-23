"""
Tests for Voice Agent Microservice (Port 8084).
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
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
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
    assert len(session.transcript) >= 6  # 3 agent turns + 3 prospect turns


@pytest.mark.asyncio
async def test_voice_agent_api_simulation_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {
            "company_name": "Gouden Draak",
            "has_website": True,
            "simulated_prospect_responses": [
                "Yes, who is this?",
                "I'm interested, send over the details.",
                "Friday morning works for a quick call.",
            ],
        }
        res = await client.post("/api/v1/voice/simulate-call", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "COMPLETED"
        assert data["disposition"] == "MEETING_BOOKED"
        assert "transcript" in data
