"""
Unit and Integration Tests for Voice Agent Real Telephony & Media Streams.
"""

import asyncio
import json
import pytest
import sniffio
from httpx import ASGITransport, AsyncClient
from MicroServices.Voice_Agent.audio_utils import AudioUtils
from MicroServices.Voice_Agent.config.settings import VoiceSettings, get_voice_settings
from MicroServices.Voice_Agent.server import app
from MicroServices.Voice_Agent.twilio_controller import TwilioController
from MicroServices.Voice_Agent.vad import VoiceActivityDetector
from MicroServices.Voice_Agent.voice_engine import VoiceEngine


@pytest.fixture(autouse=True)
def set_sniffio_asyncio_context():
    token = sniffio.current_async_library_cvar.set("asyncio")
    try:
        yield
    finally:
        sniffio.current_async_library_cvar.reset(token)


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


def test_audio_utils_mulaw_codec():
    """Test 8kHz mulaw encoding, decoding, and base64 framing."""
    silence_mulaw = AudioUtils.create_silence_mulaw(20)  # 20ms = 160 bytes
    assert len(silence_mulaw) == 160

    # Test base64 roundtrip
    b64 = AudioUtils.mulaw_to_base64(silence_mulaw)
    assert isinstance(b64, str)
    decoded_mulaw = AudioUtils.base64_to_mulaw(b64)
    assert decoded_mulaw == silence_mulaw

    # Test PCM conversion
    pcm16 = AudioUtils.mulaw_to_pcm16(silence_mulaw)
    assert len(pcm16) == 320  # 16-bit PCM = 2 bytes per sample

    # Test mulaw re-encoding
    re_mulaw = AudioUtils.pcm16_to_mulaw(pcm16)
    assert len(re_mulaw) == 160

    # Test resampling
    resampled = AudioUtils.resample(pcm16, in_rate=8000, out_rate=16000)
    assert len(resampled) in (638, 640)

    # Test RMS energy
    energy = AudioUtils.calculate_rms_energy(pcm16)
    assert isinstance(energy, float)


def test_vad_and_barge_in():
    """Test Voice Activity Detection and Barge-In interruption triggering."""
    barge_in_fired = []

    def on_barge_in():
        barge_in_fired.append(True)

    vad = VoiceActivityDetector(
        energy_threshold=100.0,
        speech_onset_frames=2,
        silence_cutoff_frames=3,
        on_barge_in=on_barge_in,
    )

    # 1. Feed silence
    silence_frame = AudioUtils.create_silence_mulaw(20)
    res = vad.process_frame(silence_frame)
    assert res["is_speech"] is False
    assert res["speech_started"] is False

    # 2. Feed speech frame (high energy signal)
    speech_pcm = (b"\x7f\x00" * 80) + (b"\x80\xff" * 80)
    speech_mulaw = AudioUtils.pcm16_to_mulaw(speech_pcm)

    res1 = vad.process_frame(speech_mulaw)
    res2 = vad.process_frame(speech_mulaw)
    assert res2["speech_started"] is True

    # 3. Test Barge-In while agent is speaking
    vad.set_agent_speaking_state(True)
    res3 = vad.process_frame(speech_mulaw)
    assert res3["barge_in_triggered"] is True
    assert len(barge_in_fired) > 0


def test_twilio_controller_twiml_generation():
    """Test TwiML XML generator with Native Speech Gather."""
    controller = TwilioController()
    twiml = controller.generate_twiml_response(
        lead_id="lead_test_123",
        company_name="Acme Roofing",
        contact_name="Bob Smith",
        has_website=False,
    )
    assert '<?xml version="1.0" encoding="UTF-8"?>' in twiml
    assert "<Response>" in twiml
    assert "<Gather" in twiml
    assert 'input="speech"' in twiml
    assert "<Say" in twiml


@pytest.mark.asyncio
async def test_voice_agent_api_endpoints(client):
    """Test Voice Agent FastAPI endpoints."""
    # 1. Health check
    res = await client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["service"] == "voice_agent"
    assert "twilio_configured" in data

    # 2. Config status
    config_res = await client.get("/api/v1/voice/config")
    assert config_res.status_code == 200
    cfg = config_res.json()
    assert "public_base_url" in cfg
    assert "tts_voice" in cfg

    # 3. TwiML endpoint
    twiml_res = await client.get("/api/v1/voice/twiml?company_name=Test+Co&has_website=true")
    assert twiml_res.status_code == 200
    assert "application/xml" in twiml_res.headers["content-type"]
    assert "<Response>" in twiml_res.text
    assert "<Gather" in twiml_res.text

    # 4. Status callback
    status_res = await client.post(
        "/api/v1/voice/status-callback",
        data={"CallSid": "CA123456789", "CallStatus": "completed", "CallDuration": "45"},
    )
    assert status_res.status_code == 200
    assert status_res.json()["status"] == "received"

    # 5. Outbound initiate without credentials returns 400 with helpful guide
    call_res = await client.post(
        "/api/v1/voice/call/initiate",
        json={"to_phone": "+15551234567", "company_name": "Test Co"},
    )
    # If credentials not set in test environment, expect 400 with TWILIO_NOT_CONFIGURED
    if not get_voice_settings().TWILIO_ACCOUNT_SID:
        assert call_res.status_code == 400
        assert call_res.json()["detail"]["error"] == "TWILIO_NOT_CONFIGURED"

    # 6. Simulated call endpoint works
    sim_res = await client.post(
        "/api/v1/voice/simulate-call",
        json={
            "company_name": "Test Corp",
            "contact_name": "Alice",
            "has_website": True,
            "simulated_prospect_responses": ["Yes, tell me more", "Thursday at 2 PM"],
        },
    )
    assert sim_res.status_code == 200
    sim_data = sim_res.json()
    assert sim_data["status"] == "COMPLETED"
    assert len(sim_data["transcript"]) >= 4

    # 7. A2A Agent Card
    card_res = await client.get("/.well-known/agent.json")
    assert card_res.status_code == 200
    card = card_res.json()
    assert card["name"] == "VoiceAgent"
    assert any(c["name"] == "initiate_real_phone_call" for c in card["capabilities"])
