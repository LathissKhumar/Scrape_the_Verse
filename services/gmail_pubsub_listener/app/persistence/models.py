"""Database and domain models for the persistence layer."""
from datetime import datetime, timezone
from typing import Optional, List
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
    last_sync_at: Optional[str] = None
    status: str = "IDLE"


class EmailMessage(BaseModel):
    id: str  # Generated unique internal ID or hash
    thread_id: Optional[str] = None
    mailbox: str = "INBOX"
    uid: int = 0

    sender_email: str
    sender_name: Optional[str] = None

    to: List[str] = Field(default_factory=list)
    cc: List[str] = Field(default_factory=list)
    bcc: List[str] = Field(default_factory=list)

    subject: Optional[str] = None
    text_body: Optional[str] = None
    html_body: Optional[str] = None

    received_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    message_id_header: Optional[str] = None
    in_reply_to: Optional[str] = None
    references: List[str] = Field(default_factory=list)

    labels: List[str] = Field(default_factory=list)
    raw_hash: Optional[str] = None
    created_at: str = Field(default_factory=utc_now_iso)


class EmailThread(BaseModel):
    thread_id: str
    lead_id: Optional[str] = None
    subject: Optional[str] = None
    participants: List[str] = Field(default_factory=list)
    message_ids: List[str] = Field(default_factory=list)
    last_message_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "ACTIVE"  # ACTIVE, WAITING_FOR_PROSPECT, WAITING_FOR_AGENCY, CLOSED


class ClassificationRecord(BaseModel):
    message_id: str
    intent: str
    confidence: float
    reason: str
    suggested_action: Optional[str] = None
    model: str = "rules"
    created_at: str = Field(default_factory=utc_now_iso)


class EventRecord(BaseModel):
    id: str
    event_type: str
    aggregate_type: Optional[str] = None
    aggregate_id: Optional[str] = None
    payload: str  # JSON-serialized string
    status: str = "PENDING"  # PENDING, PROCESSING, COMPLETED, FAILED
    created_at: str = Field(default_factory=utc_now_iso)
    processed_at: Optional[str] = None


class OutboundMessageRecord(BaseModel):
    id: str
    lead_id: Optional[str] = None
    thread_id: Optional[str] = None
    to_address: str
    subject: str
    body_text: Optional[str] = None
    status: str = "PENDING"  # PENDING, SENT, FAILED
    provider_message_id: Optional[str] = None
    error_message: Optional[str] = None
    created_at: str = Field(default_factory=utc_now_iso)
