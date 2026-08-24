"""
Voice Agent Microservice FastAPI Server (Port 8084).
Production Real-Time AI Telephony Server using Twilio Native Carrier Speech Recognition, Multi-Turn Brain, and CRM Booking.
"""

import logging
from typing import Any

import sniffio
from fastapi import FastAPI, HTTPException, Request, Response, WebSocket, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .config.settings import get_voice_settings
from .domain.call_session import CallSession, CallStatus
from .media_stream import MediaStreamSession
from .state_machine import VoiceConversationEngine
from .telephony_adapter import TelephonyAdapter
from .twilio_controller import TwilioController

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VoiceAgentServer")

app = FastAPI(
    title="AgencyOS Voice Agent Microservice",
    description="Production-grade real-time AI telephony agent using official Twilio Python SDK.",
    version="2.0.0",
)


class SniffioASGIMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] in ("http", "websocket"):
            token = sniffio.current_async_library_cvar.set("asyncio")
            try:
                await self.app(scope, receive, send)
            finally:
                sniffio.current_async_library_cvar.reset(token)
        else:
            await self.app(scope, receive, send)


app.add_middleware(SniffioASGIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

adapter = TelephonyAdapter()
twilio_controller = TwilioController()

# Active In-Flight Call Session Engines
active_call_engines: dict[str, VoiceConversationEngine] = {}
active_call_metadata: dict[str, dict[str, Any]] = {}


class OutboundCallRequest(BaseModel):
    to_phone: str
    lead_id: str | None = None
    company_name: str | None = "Valued Prospect"
    contact_name: str | None = None
    has_website: bool = True


class SimulateCallRequest(BaseModel):
    company_name: str
    prospect_phone: str | None = None
    contact_name: str | None = None
    has_website: bool = True
    lead_id: str | None = None
    simulated_prospect_responses: list[str] | None = None


class A2AInvokeRequest(BaseModel):
    skill: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    caller_agent: str | None = "unknown"


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    settings = get_voice_settings()
    return {
        "status": "healthy",
        "service": "voice_agent",
        "port": 8084,
        "twilio_configured": twilio_controller.is_configured(),
        "tts_voice": settings.VOICE_TTS_VOICE,
        "public_url": settings.VOICE_PUBLIC_BASE_URL,
    }


@app.get("/ready", status_code=status.HTTP_200_OK)
async def ready_check():
    return {
        "status": "ready",
        "telephony": "ready",
        "vad": "ready",
        "tts": "ready",
    }


@app.get("/api/v1/voice/config")
async def get_config_status():
    """Returns Twilio configuration status and guidance."""
    settings = get_voice_settings()
    is_conf = twilio_controller.is_configured()
    return {
        "twilio_configured": is_conf,
        "twilio_phone_number": settings.TWILIO_PHONE_NUMBER if is_conf else None,
        "personal_mobile_number": settings.PERSONAL_MOBILE_NUMBER,
        "public_base_url": settings.VOICE_PUBLIC_BASE_URL,
        "tts_voice": settings.VOICE_TTS_VOICE,
        "barge_in_enabled": settings.VOICE_BARGE_IN_ENABLED,
        "setup_instructions": (
            "Twilio credentials configured and active."
            if is_conf
            else "To place real PSTN phone calls, add TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER to .env."
        ),
    }


@app.get("/.well-known/agent.json")
async def serve_voice_agent_card():
    return {
        "name": "VoiceAgent",
        "description": "Production real-time AI voice engagement bot for live PSTN phone calls, lead qualification, and calendar meeting booking.",
        "version": "2.0.0",
        "protocol": "A2A/1.0",
        "endpoints": {
            "agent_card": "http://localhost:8084/.well-known/agent.json",
            "invoke": "http://localhost:8084/a2a/invoke",
        },
        "capabilities": [
            {
                "name": "initiate_real_phone_call",
                "description": "Place a real cellular/PSTN outbound phone call to a prospect's phone number.",
                "parameters": {
                    "to_phone": "string (required)",
                    "company_name": "string (optional)",
                    "contact_name": "string (optional)",
                    "lead_id": "string (optional)",
                },
            },
            {
                "name": "engage_prospect_call",
                "description": "Execute simulated qualification call for testing and development.",
                "parameters": {
                    "company_name": "string (required)",
                    "prospect_phone": "string (optional)",
                    "contact_name": "string (optional)",
                    "has_website": "boolean (optional)",
                    "lead_id": "string (optional)",
                },
            },
        ],
    }


@app.post("/api/v1/voice/call/initiate")
async def initiate_call_endpoint(request: OutboundCallRequest):
    """
    Trigger an outbound cellular/PSTN phone call via Twilio to the destination phone number.
    """
    result = twilio_controller.initiate_outbound_call(
        to_phone=request.to_phone,
        lead_id=request.lead_id,
        company_name=request.company_name,
        contact_name=request.contact_name,
        has_website=request.has_website,
    )
    if not result.get("success"):
        raise HTTPException(
            status_code=400 if result.get("error") == "TWILIO_NOT_CONFIGURED" else 500,
            detail=result,
        )
    return result


@app.post("/api/v1/voice/call/test")
async def initiate_test_call_endpoint(request: OutboundCallRequest):
    """Initiates a simple 1-line verified test call to verify phone audio delivery."""
    settings = get_voice_settings()
    client = twilio_controller.get_twilio_client()
    if not client or not settings.TWILIO_PHONE_NUMBER:
        raise HTTPException(status_code=400, detail={"error": "TWILIO_NOT_CONFIGURED"})

    target_phone = twilio_controller.normalize_phone_number(request.to_phone)
    public_url = settings.VOICE_PUBLIC_BASE_URL.rstrip("/")
    twiml_url = f"{public_url}/api/v1/voice/test-twiml"

    try:
        call = client.calls.create(
            to=target_phone,
            from_=settings.TWILIO_PHONE_NUMBER,
            url=twiml_url,
        )
        return {
            "success": True,
            "call_sid": call.sid,
            "status": call.status,
            "type": "test_call",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})


@app.api_route("/api/v1/voice/test-twiml", methods=["GET", "POST"])
async def serve_test_twiml_endpoint():
    """Returns minimal 1-line test TwiML."""
    msg = "Hello Lathiss, this is a verified test call from AgencyOS. Your Twilio Voice telephony server is working successfully."
    xml = twilio_controller.generate_simple_test_twiml(msg)
    return Response(content=xml, media_type="application/xml")


@app.api_route("/api/v1/voice/twiml", methods=["GET", "POST"])
async def serve_twiml_endpoint(request: Request):
    """
    Initial TwiML Webhook requested by Twilio when the live PSTN call connects.
    Returns opening greeting and native Twilio <Gather input="speech">.
    """
    called_number = ""
    call_sid = ""
    if request.method == "POST":
        try:
            form = await request.form()
            called_number = form.get("Called") or form.get("To") or ""
            call_sid = form.get("CallSid") or ""
        except Exception:
            pass

    cached = (
        twilio_controller.get_pending_call(called_number) or {} if called_number else {}
    )
    lead_id = request.query_params.get("lead_id") or cached.get("lead_id")
    company_name = (
        request.query_params.get("company_name")
        or cached.get("company_name")
        or "Apex Roofing Solutions"
    )
    contact_name = (
        request.query_params.get("contact_name")
        or cached.get("contact_name")
        or "Lathiss"
    )
    has_website_val = request.query_params.get("has_website")
    if has_website_val is None:
        has_website_bool = cached.get("has_website", False)
    else:
        has_website_bool = str(has_website_val).lower() == "true"

    logger.info(
        f"Twilio Call Connected: CallSid='{call_sid}', Called='{called_number}', Company='{company_name}', Contact='{contact_name}'"
    )

    # Initialize conversational state engine for this live call
    engine = VoiceConversationEngine(
        company_name=company_name,
        contact_name=contact_name,
        has_website=has_website_bool,
    )
    if call_sid:
        active_call_engines[call_sid] = engine
        active_call_metadata[call_sid] = {
            "lead_id": lead_id,
            "company_name": company_name,
            "contact_name": contact_name,
            "has_website": has_website_bool,
            "to_phone": called_number,
        }
    if called_number:
        active_call_engines[called_number] = engine

    # Generate opening turn
    opening_text = engine.start_conversation()

    settings = get_voice_settings()
    public_url = settings.VOICE_PUBLIC_BASE_URL.rstrip("/")
    action_url = f"{public_url}/api/v1/voice/turn"

    twiml_xml = twilio_controller.generate_twiml_greeting(
        speech_text=opening_text,
        turn_action_url=action_url,
    )
    return Response(content=twiml_xml, media_type="application/xml")


@app.api_route("/api/v1/voice/turn", methods=["GET", "POST"])
async def handle_voice_turn_endpoint(request: Request):
    """
    Multi-Turn Speech Webhook called by Twilio when caller speaks.
    Receives SpeechResult, evaluates conversation state, and returns next TwiML.
    """
    form_data = {}
    if request.method == "POST":
        try:
            form_data = await request.form()
        except Exception:
            pass

    call_sid = form_data.get("CallSid") or request.query_params.get("CallSid") or ""
    called_number = form_data.get("Called") or form_data.get("To") or ""
    speech_result = (
        form_data.get("SpeechResult") or request.query_params.get("SpeechResult") or ""
    )
    confidence = form_data.get("Confidence") or "1.0"

    logger.info(
        f"Twilio Voice Turn: CallSid='{call_sid}', SpeechResult='{speech_result}', Confidence={confidence}"
    )

    # Find conversation engine
    engine = active_call_engines.get(call_sid) or active_call_engines.get(called_number)
    meta = active_call_metadata.get(call_sid) or {}

    if not engine:
        company_name = meta.get("company_name", "Valued Business")
        contact_name = meta.get("contact_name")
        has_website = meta.get("has_website", False)
        engine = VoiceConversationEngine(
            company_name=company_name,
            contact_name=contact_name,
            has_website=has_website,
        )
        if call_sid:
            active_call_engines[call_sid] = engine

    settings = get_voice_settings()
    public_url = settings.VOICE_PUBLIC_BASE_URL.rstrip("/")
    action_url = f"{public_url}/api/v1/voice/turn"

    if not speech_result.strip():
        twiml_xml = twilio_controller.generate_twiml_greeting(
            speech_text="I didn't quite hear you. Would you like us to schedule a quick 10-minute discovery demo this week?",
            turn_action_url=action_url,
        )
        return Response(content=twiml_xml, media_type="application/xml")

    # Process turn with conversation engine
    turn_result = await engine.process_turn_async(speech_result)
    agent_reply = turn_result["agent_response"]
    new_state = turn_result["new_state"]

    logger.info(f"AI Agent Reply: '{agent_reply}' (New State: {new_state})")

    is_terminal = new_state in ("BOOKING", "NOT_INTERESTED", "CLOSING")

    if is_terminal:
        # Sync final session to Lead Manager CRM (:8082)
        lead_id = meta.get("lead_id")
        session = CallSession(
            lead_id=lead_id,
            company_name=engine.company_name,
            contact_name=engine.contact_name,
            status=CallStatus.COMPLETED,
            disposition=engine.disposition,
            interest_score=engine.interest_score,
            transcript=engine.transcript,
            call_summary=(
                f"Live PSTN phone call with {engine.company_name} ({engine.contact_name or 'Owner'}). "
                f"Disposition: {engine.disposition.value if engine.disposition else 'COMPLETED'}. "
                f"Interest Score: {engine.interest_score}/100."
            ),
            booked_meeting_time=engine.booked_meeting_time,
            metadata={"call_sid": call_sid, "has_website": engine.has_website},
        )
        await adapter.sync_session_to_lead_manager(session)

        twiml_xml = twilio_controller.generate_twiml_terminal(closing_text=agent_reply)
        return Response(content=twiml_xml, media_type="application/xml")

    # Ongoing turn: generate next <Gather input="speech">
    twiml_xml = twilio_controller.generate_twiml_greeting(
        speech_text=agent_reply,
        turn_action_url=action_url,
    )
    return Response(content=twiml_xml, media_type="application/xml")


@app.api_route("/api/v1/voice/status-callback", methods=["POST"])
async def status_callback_endpoint(request: Request):
    """
    Receives Twilio call status updates (ringing, answered, completed, busy).
    """
    form_data = await request.form()
    call_sid = form_data.get("CallSid")
    call_status = form_data.get("CallStatus")
    duration = form_data.get("CallDuration")
    logger.info(
        f"Twilio Status Callback: CallSid={call_sid}, Status={call_status}, Duration={duration}s"
    )

    if (
        call_status in ("completed", "canceled", "failed", "busy", "no-answer")
        and call_sid in active_call_engines
    ):
        active_call_engines.pop(call_sid, None)
        active_call_metadata.pop(call_sid, None)

    return {"status": "received", "call_sid": call_sid}


@app.websocket("/api/v1/voice/stream")
async def websocket_media_stream_endpoint(websocket: WebSocket):
    """
    Bi-directional full-duplex WebSocket endpoint for Twilio Media Streams.
    """
    session = MediaStreamSession(websocket=websocket, telephony_adapter=adapter)
    await session.handle_stream()


@app.post("/api/v1/voice/simulate-call", response_model=CallSession)
async def simulate_call_endpoint(request: SimulateCallRequest):
    """Run a simulated multi-turn phone conversation for testing."""
    session = await adapter.simulate_call(
        company_name=request.company_name,
        prospect_phone=request.prospect_phone,
        contact_name=request.contact_name,
        has_website=request.has_website,
        lead_id=request.lead_id,
        simulated_prospect_responses=request.simulated_prospect_responses,
    )
    return session


@app.post("/a2a/invoke")
async def invoke_a2a_skill(request: A2AInvokeRequest):
    """Execute A2A capability on Voice Agent."""
    skill = request.skill
    params = request.parameters

    if skill in ("initiate_real_phone_call", "make_outbound_call"):
        res = twilio_controller.initiate_outbound_call(
            to_phone=params.get("to_phone", ""),
            lead_id=params.get("lead_id"),
            company_name=params.get("company_name"),
            contact_name=params.get("contact_name"),
            has_website=params.get("has_website", True),
        )
        return {"success": res.get("success", False), "result": res}
    elif skill == "engage_prospect_call":
        session = await adapter.simulate_call(
            company_name=params.get("company_name", "Unknown Business"),
            prospect_phone=params.get("prospect_phone"),
            contact_name=params.get("contact_name"),
            has_website=params.get("has_website", True),
            lead_id=params.get("lead_id"),
        )
        return {"success": True, "result": session.model_dump()}
    else:
        raise HTTPException(status_code=400, detail=f"Unknown skill '{skill}'")
