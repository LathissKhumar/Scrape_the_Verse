"""Database and domain models for the persistence layer."""

from datetime import datetime, timezone

from pydantic import BaseModel, Field


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class GmailAccountRecord(BaseModel):
    id: str
    email: str
    status: str = "ACTIVE"
    created_at: str = Field(default_factory=utc_now_iso)
    updated_at: str = Field(default_factory=utc_now_iso)


class MailboxStateRecord(BaseModel):
    mailbox: str = "INBOX"
    last_uid: int = 0
    last_sync_at: str | None = None
    status: str = "IDLE"


class EmailMessage(BaseModel):
    id: str  # Generated unique internal ID or hash
    thread_id: str | None = None
    mailbox: str = "INBOX"
    uid: int = 0

    sender_email: str
    sender_name: str | None = None

    to: list[str] = Field(default_factory=list)
    cc: list[str] = Field(default_factory=list)
    bcc: list[str] = Field(default_factory=list)

    subject: str | None = None
    text_body: str | None = None
    html_body: str | None = None

    received_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    message_id_header: str | None = None
    in_reply_to: str | None = None
    references: list[str] = Field(default_factory=list)

    labels: list[str] = Field(default_factory=list)
    raw_hash: str | None = None
    created_at: str = Field(default_factory=utc_now_iso)


class EmailThread(BaseModel):
    thread_id: str
    lead_id: str | None = None
    subject: str | None = None
    participants: list[str] = Field(default_factory=list)
    message_ids: list[str] = Field(default_factory=list)
    last_message_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    status: str = "ACTIVE"  # ACTIVE, WAITING_FOR_PROSPECT, WAITING_FOR_AGENCY, CLOSED


class ClassificationRecord(BaseModel):
    message_id: str
    intent: str
    confidence: float
    reason: str
    suggested_action: str | None = None
    model: str = "rules"
    created_at: str = Field(default_factory=utc_now_iso)


class EventRecord(BaseModel):
    id: str
    event_type: str
    aggregate_type: str | None = None
    aggregate_id: str | None = None
    payload: str  # JSON-serialized string
    status: str = "PENDING"  # PENDING, PROCESSING, COMPLETED, FAILED
    created_at: str = Field(default_factory=utc_now_iso)
    processed_at: str | None = None


class OutboundMessageRecord(BaseModel):
    id: str
    lead_id: str | None = None
    thread_id: str | None = None
    to_address: str
    subject: str
    body_text: str | None = None
    status: str = "PENDING"  # PENDING, SENT, FAILED
    provider_message_id: str | None = None
    error_message: str | None = None
    created_at: str = Field(default_factory=utc_now_iso)
