"""Autonomous Auto-Responder Engine for instant thread-aware replies."""

import logging

import httpx

from app.config import get_settings
from app.events.models import CommunicationEvent
from app.persistence.repository import Repository
from app.persistence.repository import repository as default_repo
from app.smtp.sender import (
    GmailSMTPSender,
    OutboundEmail,
)
from app.smtp.sender import (
    smtp_sender as default_sender,
)

logger = logging.getLogger(__name__)


class AutoResponder:
    def __init__(
        self,
        repo: Repository | None = None,
        sender: GmailSMTPSender | None = None,
    ):
        self.repo = repo or default_repo
        self.sender = sender or default_sender
        self.settings = get_settings()

    async def handle_new_inbound(self, event: CommunicationEvent) -> None:
        """Evaluates incoming message and triggers an autonomous reply within seconds."""
        if not self.settings.AUTO_REPLY_ENABLED:
            return

        payload = event.payload
        message_id = payload.get("message_id")
        thread_id = payload.get("thread_id")
        sender_email = payload.get("sender_email")
        subject = payload.get("subject", "")

        # Safety checks
        my_email = self.settings.GMAIL_ADDRESS.lower().strip()
        if not sender_email or sender_email.lower().strip() == my_email:
            return

        # Skip automated notifications & bots
        if any(
            bot in sender_email.lower()
            for bot in ["noreply", "no-reply", "mailer-daemon", "notifications@"]
        ):
            return

        # Fetch message and classification
        message = await self.repo.get_message(message_id)
        if not message:
            return

        classification = await self.repo.get_classification(message_id)
        intent = classification.intent if classification else "UNKNOWN"

        # Do not reply to OOO, Bounces, or Unsubscribes
        if intent in ["OUT_OF_OFFICE", "BOUNCE", "UNSUBSCRIBE"]:
            logger.info(
                f"AutoResponder skipped intent '{intent}' for message {message_id}."
            )
            return

        logger.info(
            f"AutoResponder generating instant reply for {sender_email} (intent: {intent})..."
        )

        # Generate intelligent reply body
        reply_body = await self._generate_reply_content(
            message.text_body or "", intent, message.sender_name
        )

        # Send thread-aware reply
        reply_req = OutboundEmail(
            to=[sender_email],
            subject=f"Re: {subject}"
            if not subject.lower().startswith("re:")
            else subject,
            body_text=reply_body,
            thread_id=thread_id,
            in_reply_to=message.message_id_header,
        )

        res = await self.sender.send(reply_req)
        if res.status == "sent":
            logger.info(
                f"AutoResponder successfully delivered reply to {sender_email} on thread {thread_id}!"
            )
        else:
            logger.warning(f"AutoResponder failed to send reply: {res.error}")

    async def _generate_reply_content(
        self, inbound_text: str, intent: str, sender_name: str | None
    ) -> str:
        name_greeting = (
            f"Hi {sender_name.split()[0]},\n\n" if sender_name else "Hello,\n\n"
        )

        # Try generating customized AI response via local Ollama if running
        ai_reply = await self._generate_ai_reply(inbound_text, intent, sender_name)
        if ai_reply:
            return ai_reply

        # Fallback tailored responses based on intent
        if intent == "REQUEST_MEETING":
            return (
                f"{name_greeting}"
                "Thank you for reaching out! We would be glad to discuss this further.\n\n"
                "You can pick a convenient time on our calendar here: https://cal.com/agencyos-demo\n\n"
                "Looking forward to connecting!\n\n"
                "Best regards,\n"
                "AgencyOS Automated Assistant"
            )
        elif intent == "REQUEST_PRICING":
            return (
                f"{name_greeting}"
                "Thank you for your inquiry about our pricing and services.\n\n"
                "Our agency packages typically range depending on project scope and deliverables. "
                "I have forwarded your request to our team to prepare a detailed quote for you.\n\n"
                "Best regards,\n"
                "AgencyOS Automated Assistant"
            )
        else:
            return (
                f"{name_greeting}"
                "Thank you for your message!\n\n"
                "This email is to confirm that our automated system received your inquiry. "
                "Our team will review your message and get back to you promptly.\n\n"
                "Best regards,\n"
                "AgencyOS Automated Assistant"
            )

    async def _generate_ai_reply(
        self, inbound_text: str, intent: str, sender_name: str | None
    ) -> str | None:
        prompt = (
            f"You are an AI sales assistant for an agency. Write a concise, polite, professional, "
            f"and helpful email reply (2-4 sentences max) to this email:\n\n"
            f"Sender Name: {sender_name or 'Friend'}\n"
            f"Customer Intent: {intent}\n"
            f"Email content: {inbound_text}\n\n"
            f"Do not include placeholders like [Your Name]. Sign off as 'AgencyOS Assistant'."
        )

        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                res = await client.post(
                    f"{self.settings.OLLAMA_BASE_URL.rstrip('/')}/api/chat",
                    json={
                        "model": self.settings.OLLAMA_MODEL,
                        "messages": [{"role": "user", "content": prompt}],
                        "stream": False,
                    },
                )
                if res.status_code == 200:
                    content = res.json().get("message", {}).get("content", "").strip()
                    if content:
                        return content
        except Exception:
            pass
        return None


auto_responder = AutoResponder()
