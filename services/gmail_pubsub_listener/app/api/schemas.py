"""Pydantic request and response schemas for REST API."""

from typing import Any

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    service: str = "communication_service"
    imap_connected: bool
    listener_running: bool
    version: str = "1.0.0"


class MailboxStatusResponse(BaseModel):
    mailbox: str
    status: str
    last_uid: int
    last_sync_at: str | None
    imap_host: str
    listener_active: bool


class SyncRequest(BaseModel):
    mailbox: str = "INBOX"


class SyncResponse(BaseModel):
    status: str
    synced_messages_count: int
    mailbox: str


class SendMailRequest(BaseModel):
    lead_id: str | None = None
    thread_id: str | None = None
    to: list[str]
    subject: str
    body_text: str
    body_html: str | None = None
    cc: list[str] = Field(default_factory=list)
    bcc: list[str] = Field(default_factory=list)
    in_reply_to: str | None = None
    references: list[str] = Field(default_factory=list)


class SendMailResponse(BaseModel):
    status: str
    message_id: str
    provider_message_id: str | None = None
    sent_at: str
    error: str | None = None


class TimelineMessage(BaseModel):
    id: str
    direction: str  # INBOUND or OUTBOUND
    sender: str
    subject: str | None = None
    body: str | None = None
    timestamp: str
    intent: str | None = None
    confidence: float | None = None
    status: str | None = None


class ThreadDetailResponse(BaseModel):
    thread_id: str
    lead_id: str | None = None
    subject: str | None = None
    participants: list[str] = Field(default_factory=list)
    status: str
    messages: list[TimelineMessage] = Field(default_factory=list)


class A2AInvokeRequest(BaseModel):
    skill: str
    parameters: dict[str, Any] = Field(default_factory=dict)
