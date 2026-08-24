"""SMTP email sender supporting thread-aware replies and TLS."""

import asyncio
import email.message
import email.utils
import logging
import smtplib
import ssl
import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, Field

from app.config import get_settings
from app.events.bus import EventBus
from app.events.bus import event_bus as default_bus
from app.events.models import CommunicationEvent, EventTypes
from app.persistence.models import OutboundMessageRecord
from app.persistence.repository import Repository
from app.persistence.repository import repository as default_repo

logger = logging.getLogger(__name__)


class OutboundEmail(BaseModel):
    to: list[str]
    subject: str
    body_text: str
    body_html: str | None = None
    cc: list[str] = Field(default_factory=list)
    bcc: list[str] = Field(default_factory=list)
    lead_id: str | None = None
    thread_id: str | None = None
    in_reply_to: str | None = None
    references: list[str] = Field(default_factory=list)


class SendResult(BaseModel):
    status: str
    message_id: str
    provider_message_id: str | None = None
    sent_at: str
    error: str | None = None


class GmailSMTPSender:
    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        email_address: str | None = None,
        password: str | None = None,
        repo: Repository | None = None,
        bus: EventBus | None = None,
    ):
        settings = get_settings()
        self.host = host or settings.SMTP_SERVER
        self.port = port or settings.SMTP_PORT
        self.email_address = email_address or settings.GMAIL_ADDRESS
        self.password = password or settings.GMAIL_APP_PASSWORD
        self.repo = repo or default_repo
        self.bus = bus or default_bus

    async def send(self, email_req: OutboundEmail) -> SendResult:
        """Sends an outbound email via Gmail SMTP with thread headers."""
        msg_id = f"out_{uuid.uuid4().hex[:12]}"
        now_str = datetime.now(timezone.utc).isoformat()

        # Check if thread_id is given to look up reply headers
        in_reply_to = email_req.in_reply_to
        references = list(email_req.references)

        if email_req.thread_id and not in_reply_to:
            thread_messages = await self.repo.get_messages_by_thread(
                email_req.thread_id
            )
            if thread_messages:
                last_msg = thread_messages[-1]
                if last_msg.message_id_header:
                    in_reply_to = last_msg.message_id_header
                    if last_msg.message_id_header not in references:
                        references.append(last_msg.message_id_header)

        # Build RFC message
        msg = email.message.EmailMessage()
        msg["From"] = self.email_address
        msg["To"] = ", ".join(email_req.to)
        if email_req.cc:
            msg["Cc"] = ", ".join(email_req.cc)
        if email_req.bcc:
            msg["Bcc"] = ", ".join(email_req.bcc)
        msg["Subject"] = email_req.subject
        msg["Date"] = email.utils.formatdate(localtime=True)
        msg["Message-ID"] = email.utils.make_msgid(
            domain=self.email_address.split("@")[-1]
            if "@" in self.email_address
            else "gmail.com"
        )

        if in_reply_to:
            msg["In-Reply-To"] = f"<{in_reply_to.strip('<>')}>"
        if references:
            msg["References"] = " ".join(f"<{r.strip('<>')}>" for r in references)

        # Set content
        msg.set_content(email_req.body_text)
        if email_req.body_html:
            msg.add_alternative(email_req.body_html, subtype="html")

        # Save initial outbound record
        outbound_record = OutboundMessageRecord(
            id=msg_id,
            lead_id=email_req.lead_id,
            thread_id=email_req.thread_id,
            to_address=", ".join(email_req.to),
            subject=email_req.subject,
            body_text=email_req.body_text,
            status="PENDING",
            provider_message_id=msg["Message-ID"],
            created_at=now_str,
        )
        await self.repo.save_outbound_message(outbound_record)

        # Perform SMTP transmission in thread
        try:
            await asyncio.to_thread(
                self._transmit_smtp, msg, email_req.to + email_req.cc + email_req.bcc
            )

            outbound_record.status = "SENT"
            await self.repo.save_outbound_message(outbound_record)

            # Publish event
            await self.bus.publish(
                CommunicationEvent(
                    event_type=EventTypes.EMAIL_SENT.value,
                    aggregate_type="outbound_message",
                    aggregate_id=msg_id,
                    payload={
                        "id": msg_id,
                        "lead_id": email_req.lead_id,
                        "thread_id": email_req.thread_id,
                        "to": email_req.to,
                        "subject": email_req.subject,
                        "message_id_header": msg["Message-ID"],
                        "sent_at": now_str,
                    },
                )
            )

            return SendResult(
                status="sent",
                message_id=msg_id,
                provider_message_id=msg["Message-ID"],
                sent_at=now_str,
            )

        except Exception as e:
            logger.error(f"Failed to send email via SMTP: {e}", exc_info=True)
            outbound_record.status = "FAILED"
            outbound_record.error_message = str(e)
            await self.repo.save_outbound_message(outbound_record)

            await self.bus.publish(
                CommunicationEvent(
                    event_type=EventTypes.EMAIL_DELIVERY_FAILED.value,
                    aggregate_type="outbound_message",
                    aggregate_id=msg_id,
                    payload={"id": msg_id, "error": str(e)},
                )
            )

            return SendResult(
                status="failed",
                message_id=msg_id,
                sent_at=now_str,
                error=str(e),
            )

    def _get_oauth2_access_token(self) -> str | None:
        """Fetches a fresh access token using the OAuth refresh token."""
        settings = get_settings()
        if not (
            settings.GOOGLE_CLIENT_ID
            and settings.GOOGLE_CLIENT_SECRET
            and settings.GOOGLE_REFRESH_TOKEN
        ):
            return None
        try:
            import httpx

            resp = httpx.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "refresh_token": settings.GOOGLE_REFRESH_TOKEN,
                    "grant_type": "refresh_token",
                },
                timeout=10.0,
            )
            if resp.status_code == 200:
                return resp.json().get("access_token")
        except Exception as e:
            logger.warning(f"Failed to refresh OAuth token for SMTP: {e}")
        return None

    def _transmit_smtp(
        self, msg: email.message.EmailMessage, recipients: list[str]
    ) -> None:
        settings = get_settings()
        email_address = self.email_address or settings.GMAIL_ADDRESS
        password = self.password or settings.GMAIL_APP_PASSWORD

        if not email_address:
            raise ValueError("Gmail address must be configured to send emails.")

        clean_pwd = (password or "").replace(" ", "")
        access_token = self._get_oauth2_access_token() if not clean_pwd else None

        if self.port == 465:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(self.host, self.port, context=context) as server:
                if clean_pwd:
                    server.login(email_address, clean_pwd)
                elif access_token:
                    auth_string = (
                        f"user={email_address}\x01auth=Bearer {access_token}\x01\x01"
                    )
                    server.auth("XOAUTH2", lambda: auth_string)
                else:
                    raise ValueError("No valid credentials for SMTP transmission.")
                server.send_message(msg, to_addrs=recipients)
        else:
            with smtplib.SMTP(self.host, self.port) as server:
                server.starttls()
                if clean_pwd:
                    server.login(email_address, clean_pwd)
                elif access_token:
                    auth_string = (
                        f"user={email_address}\x01auth=Bearer {access_token}\x01\x01"
                    )
                    server.auth("XOAUTH2", lambda: auth_string)
                else:
                    raise ValueError("No valid credentials for SMTP transmission.")
                server.send_message(msg, to_addrs=recipients)


smtp_sender = GmailSMTPSender()
