"""
Twilio PSTN Telephony Controller & Official TwiML Generator.
Built strictly adhering to Twilio Python SDK documentation & best practices.
"""

import logging
import re
from typing import Any

from twilio.rest import Client
from twilio.twiml.voice_response import Gather, Hangup, VoiceResponse

from .config.settings import get_voice_settings

logger = logging.getLogger("TwilioController")


class TwilioController:
    """
    Manages Twilio REST API interactions, outbound call creation, and TwiML generation.
    """

    def __init__(self):
        self._pending_calls: dict[str, dict[str, Any]] = {}

    def is_configured(self) -> bool:
        """Check whether valid Twilio credentials exist in the environment."""
        settings = get_voice_settings()
        return bool(
            settings.TWILIO_ACCOUNT_SID
            and settings.TWILIO_AUTH_TOKEN
            and settings.TWILIO_PHONE_NUMBER
        )

    def get_twilio_client(self) -> Client | None:
        """Initializes and returns the official Twilio REST Client."""
        settings = get_voice_settings()
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            return Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        return None

    @staticmethod
    def normalize_phone_number(phone: str) -> str:
        """
        Normalizes a phone number into strict E.164 format (+XXXXXXXXXXX).
        """
        cleaned = re.sub(r"[^\d+]", "", phone.strip())
        if not cleaned:
            return ""
        if cleaned.startswith("+"):
            return cleaned
        # Indian 10-digit mobile
        if len(cleaned) == 10 and cleaned[0] in "6789":
            return f"+91{cleaned}"
        # US/Canada 10-digit
        if len(cleaned) == 10:
            return f"+1{cleaned}"
        if len(cleaned) == 12 and cleaned.startswith("91"):
            return f"+{cleaned}"
        if len(cleaned) == 11 and cleaned.startswith("1"):
            return f"+{cleaned}"
        return f"+{cleaned}"

    def register_pending_call(self, phone: str, data: dict[str, Any]) -> None:
        """Stores lead and prospect metadata for retrieval when Twilio hits the webhook."""
        normalized = self.normalize_phone_number(phone)
        self._pending_calls[normalized] = data

    def get_pending_call(self, phone: str) -> dict[str, Any] | None:
        """Retrieves prospect metadata for a given phone number."""
        normalized = self.normalize_phone_number(phone)
        return self._pending_calls.get(normalized)

    def generate_twiml_greeting(
        self,
        speech_text: str,
        turn_action_url: str,
    ) -> str:
        """
        Generates official TwiML containing <Say> wrapped in <Gather input="speech">.
        When caller speaks, Twilio transcribes audio and sends text to turn_action_url.
        """
        response = VoiceResponse()
        gather = Gather(
            input="speech",
            action=turn_action_url,
            method="POST",
            speech_timeout="auto",
            timeout=4,
            language="en-US",
        )
        gather.say(speech_text, voice="alice", language="en-US")
        response.append(gather)

        # Fallback if no speech is detected after timeout
        response.say(
            "Thank you for your time. Have a wonderful day!",
            voice="alice",
            language="en-US",
        )
        response.append(Hangup())
        return str(response)

    def generate_simple_test_twiml(self, text: str) -> str:
        """Generates a minimal 1-line test TwiML for verifying carrier voice reachability."""
        response = VoiceResponse()
        response.say(text, voice="alice", language="en-US")
        response.append(Hangup())
        return str(response)

    def generate_twiml_terminal(self, closing_text: str) -> str:
        """
        Generates official terminal TwiML to deliver final confirmation and hang up.
        """
        response = VoiceResponse()
        response.say(closing_text, voice="alice", language="en-US")
        response.append(Hangup())
        return str(response)

    def generate_twiml_response(
        self,
        lead_id: str | None = None,
        company_name: str | None = None,
        contact_name: str | None = None,
        has_website: bool = True,
    ) -> str:
        """
        Standard initial TwiML generator matching test suite and runtime callers.
        """
        settings = get_voice_settings()
        public_url = settings.VOICE_PUBLIC_BASE_URL.rstrip("/")
        turn_url = f"{public_url}/api/v1/voice/turn"

        greeting = (
            f"Hello {contact_name or 'there'}, this is Sarah with the AgencyOS Growth team. "
            f"I'm reaching out because we noticed {company_name or 'your company'} does not currently have a mobile-verified website. "
            f"Do you have 30 seconds to speak with me?"
        )
        return self.generate_twiml_greeting(
            speech_text=greeting, turn_action_url=turn_url
        )

    def initiate_outbound_call(
        self,
        to_phone: str,
        lead_id: str | None = None,
        company_name: str | None = None,
        contact_name: str | None = None,
        has_website: bool = True,
    ) -> dict[str, Any]:
        """
        Creates and dispatches an outbound call via Twilio REST API.
        """
        settings = get_voice_settings()
        client = self.get_twilio_client()
        if not client or not settings.TWILIO_PHONE_NUMBER:
            return {
                "success": False,
                "error": "TWILIO_NOT_CONFIGURED",
                "message": "Twilio credentials missing or incomplete in environment.",
            }

        target_phone = self.normalize_phone_number(to_phone)
        self.register_pending_call(
            target_phone,
            {
                "lead_id": lead_id,
                "company_name": company_name,
                "contact_name": contact_name,
                "has_website": has_website,
            },
        )

        # Build high-reliability Twilio-hosted multi-turn conversation URL
        from .twimlet_builder import build_conversation_tree

        twiml_url = build_conversation_tree(
            company_name=company_name or "Apex Roofing Solutions",
            contact_name=contact_name or "Valued Business",
            has_website=has_website,
        )

        logger.info(
            f"Initiating outbound call to {target_phone} via Twimlet Tree (len={len(twiml_url)})"
        )
        try:
            call = client.calls.create(
                to=target_phone,
                from_=settings.TWILIO_PHONE_NUMBER,
                url=twiml_url,
            )
            return {
                "success": True,
                "call_sid": call.sid,
                "to_phone": target_phone,
                "from_phone": settings.TWILIO_PHONE_NUMBER,
                "status": call.status,
                "lead_id": lead_id,
            }
        except Exception as e:
            logger.error(f"Failed to initiate Twilio call: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Twilio call dispatch failed: {e}",
            }
