"""Pydantic request and response schemas for REST API."""
from datetime import datetime
from typing import Any, Dict, List, Optional
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
    last_sync_at: Optional[str]
    imap_host: str
    listener_active: bool


class SyncRequest(BaseModel):
    mailbox: str = "INBOX"


class SyncResponse(BaseModel):
    status: str
    synced_messages_count: int
    mailbox: str


class SendMailRequest(BaseModel):
    lead_id: Optional[str] = None
    thread_id: Optional[str] = None
    to: List[str]
    subject: str
    body_text: str
    body_html: Optional[str] = None
    cc: List[str] = Field(default_factory=list)
    bcc: List[str] = Field(default_factory=list)
    in_reply_to: Optional[str] = None
    references: List[str] = Field(default_factory=list)


class SendMailResponse(BaseModel):
    status: str
    message_id: str
    provider_message_id: Optional[str] = None
    sent_at: str
    error: Optional[str] = None


class TimelineMessage(BaseModel):
    id: str
    direction: str  # INBOUND or OUTBOUND
    sender: str
    subject: Optional[str] = None
    body: Optional[str] = None
    timestamp: str
    intent: Optional[str] = None
    confidence: Optional[float] = None
    status: Optional[str] = None


class ThreadDetailResponse(BaseModel):
    thread_id: str
    lead_id: Optional[str] = None
    subject: Optional[str] = None
    participants: List[str] = Field(default_factory=list)
    status: str
    messages: List[TimelineMessage] = Field(default_factory=list)


class A2AInvokeRequest(BaseModel):
    skill: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
