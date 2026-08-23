"""
Twilio Bi-Directional WebSocket Media Stream Handler.
Full-duplex real-time audio pipeline: mulaw 8000Hz -> VAD -> STT -> LLM Dialogue -> Edge-TTS -> mulaw 8000Hz.
"""

import asyncio
import json
import logging
import urllib.parse
from typing import Optional
from fastapi import WebSocket, WebSocketDisconnect
from .audio_utils import AudioUtils
from .domain.call_session import CallSession, CallStatus, CallTurn
from .state_machine import VoiceConversationEngine
from .telephony_adapter import TelephonyAdapter
from .vad import VoiceActivityDetector
from .voice_engine import VoiceEngine

logger = logging.getLogger("MediaStreamHandler")


class MediaStreamSession:
    """
    Manages a single live telephony call audio stream connected via Twilio Media Streams.
    """

    def __init__(self, websocket: WebSocket, telephony_adapter: TelephonyAdapter):
        self.websocket = websocket
        self.telephony_adapter = telephony_adapter
        self.stream_sid: Optional[str] = None
        self.call_sid: Optional[str] = None
        self.lead_id: Optional[str] = None
        self.company_name: str = "Valued Business"
        self.contact_name: Optional[str] = None
        self.has_website: bool = True

        self.voice_engine = VoiceEngine()
        self.vad = VoiceActivityDetector(on_barge_in=self._handle_barge_in)
        self.engine: Optional[VoiceConversationEngine] = None
        self.current_playback_task: Optional[asyncio.Task] = None
        self.is_active = True

    def _handle_barge_in(self) -> None:
        """Invoked immediately when caller speaks while AI agent is talking."""
        if self.current_playback_task and not self.current_playback_task.done():
            logger.info("Barge-In detected! Halting active agent speech playback.")
            self.current_playback_task.cancel()
            asyncio.create_task(self._send_clear_to_twilio())

    async def _send_clear_to_twilio(self) -> None:
        """Send clear event to Twilio to flush device audio playback buffer."""
        if self.stream_sid and self.is_active:
            try:
                await self.websocket.send_text(
                    json.dumps({"event": "clear", "streamSid": self.stream_sid})
                )
            except Exception:
                pass

    async def handle_stream(self) -> None:
        """Main WebSocket loop handling Twilio Media Streams protocol."""
        await self.websocket.accept()
        try:
            while self.is_active:
                message_text = await self.websocket.receive_text()
                msg = json.loads(message_text)
                event_type = msg.get("event")

                if event_type == "connected":
                    logger.info("Twilio Media Stream connected.")

                elif event_type == "start":
                    await self._handle_start_event(msg)

                elif event_type == "media":
                    await self._handle_media_event(msg)

                elif event_type == "stop":
                    logger.info("Twilio Media Stream stop event received.")
                    await self._handle_stop_event()
                    break

        except WebSocketDisconnect:
            logger.info("Twilio WebSocket disconnected.")
            await self._handle_stop_event()
        except Exception as e:
            logger.error(f"Error in MediaStreamSession: {e}")
            await self._handle_stop_event()

    async def _handle_start_event(self, msg: dict) -> None:
        """Handle 'start' event from Twilio containing metadata and custom parameters."""
        start_data = msg.get("start", {})
        self.stream_sid = start_data.get("streamSid")
        self.call_sid = start_data.get("callSid")
        custom_params = start_data.get("customParameters", {})

        self.lead_id = custom_params.get("lead_id") or None
        raw_company = custom_params.get("company_name", "Valued Business")
        self.company_name = urllib.parse.unquote_plus(raw_company)
        raw_contact = custom_params.get("contact_name")
        self.contact_name = urllib.parse.unquote_plus(raw_contact) if raw_contact else None
        self.has_website = custom_params.get("has_website", "true").lower() == "true"

        # Initialize conversation engine
        self.engine = VoiceConversationEngine(
            company_name=self.company_name,
            contact_name=self.contact_name,
            has_website=self.has_website,
        )

        logger.info(
            f"Live call stream started: CallSid={self.call_sid}, StreamSid={self.stream_sid}, "
            f"Company={self.company_name}, Contact={self.contact_name}, HasWebsite={self.has_website}"
        )

        # Generate and play initial greeting
        opening_reply = self.engine.start_conversation()
        self.current_playback_task = asyncio.create_task(self._play_speech_response(opening_reply))

    async def _handle_media_event(self, msg: dict) -> None:
        """Process incoming 20ms mulaw audio frame from caller."""
        media_data = msg.get("media", {})
        payload = media_data.get("payload", "")
        if not payload:
            return

        mulaw_bytes = AudioUtils.base64_to_mulaw(payload)
        vad_res = self.vad.process_frame(mulaw_bytes)

        if vad_res["speech_ended"] and vad_res["speech_pcm"]:
            # Caller finished speaking: transcribe and process turn
            speech_pcm = vad_res["speech_pcm"]
            user_text = await self.voice_engine.transcribe_pcm(speech_pcm)
            if user_text:
                logger.info(f"Caller Said: '{user_text}'")
                await self._process_caller_turn(user_text)

    async def _process_caller_turn(self, user_utterance: str) -> None:
        """Execute conversational brain turn and stream agent reply back to caller."""
        if not self.engine:
            return

        # Execute conversation turn
        turn_result = await self.engine.process_turn_async(user_utterance)
        agent_reply = turn_result["agent_response"]
        logger.info(f"AI Agent Response: '{agent_reply}' (State: {turn_result['new_state']})")

        # Play agent speech response
        if self.current_playback_task and not self.current_playback_task.done():
            self.current_playback_task.cancel()

        self.current_playback_task = asyncio.create_task(self._play_speech_response(agent_reply))

    async def _play_speech_response(self, text: str) -> None:
        """Synthesize text and stream mulaw frames over WebSocket to Twilio."""
        if not self.stream_sid or not text:
            return

        self.vad.set_agent_speaking_state(True)
        try:
            async for frame_b64 in self.voice_engine.stream_speech_frames(text=text):
                if not self.is_active:
                    break
                payload = {
                    "event": "media",
                    "streamSid": self.stream_sid,
                    "media": {"payload": frame_b64},
                }
                await self.websocket.send_text(json.dumps(payload))
        except asyncio.CancelledError:
            logger.info("Speech playback was interrupted by caller (barge-in).")
        except Exception as e:
            logger.error(f"Error streaming speech frame to Twilio: {e}")
        finally:
            self.vad.set_agent_speaking_state(False)

    async def _handle_stop_event(self) -> None:
        """Finalize call session, compute disposition, and sync to Lead Manager."""
        if not self.is_active:
            return
        self.is_active = False

        if self.current_playback_task and not self.current_playback_task.done():
            self.current_playback_task.cancel()

        if self.engine:
            # Build completed call session object
            session = CallSession(
                lead_id=self.lead_id,
                company_name=self.company_name,
                contact_name=self.contact_name,
                status=CallStatus.COMPLETED,
                disposition=self.engine.disposition,
                interest_score=self.engine.interest_score,
                transcript=self.engine.transcript,
                call_summary=(
                    f"Live PSTN phone call with {self.company_name} ({self.contact_name or 'Owner'}). "
                    f"Disposition: {self.engine.disposition.value if self.engine.disposition else 'COMPLETED'}. Interest Score: {self.engine.interest_score}/100."
                ),
                booked_meeting_time=self.engine.booked_meeting_time,
                metadata={"call_sid": self.call_sid, "has_website": self.has_website},
            )

            # Persist and dispatch to Lead Manager CRM (:8082)
            await self.telephony_adapter.sync_session_to_lead_manager(session)
