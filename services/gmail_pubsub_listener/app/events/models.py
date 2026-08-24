"""Event definitions and payload schemas."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class EventTypes(str, Enum):
    EMAIL_RECEIVED = "email.received"
    EMAIL_SENT = "email.sent"
    EMAIL_CLASSIFIED = "email.classified"
    THREAD_CREATED = "thread.created"
    THREAD_UPDATED = "thread.updated"
    LEAD_EMAIL_CORRELATED = "lead.email.correlated"
    LEAD_EMAIL_UNMATCHED = "lead.email.unmatched"
    EMAIL_BOUNCE = "email.bounce"
    EMAIL_UNSUBSCRIBE = "email.unsubscribe"
    EMAIL_DELIVERY_FAILED = "email.delivery_failed"


class CommunicationEvent(BaseModel):
    id: str = Field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:12]}")
    event_type: str
    aggregate_type: str | None = None
    aggregate_id: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
