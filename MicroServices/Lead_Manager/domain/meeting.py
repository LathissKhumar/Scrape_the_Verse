"""
Meeting Domain Model.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import uuid4
from pydantic import BaseModel, Field
from .stage import MeetingStatus


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class Meeting(BaseModel):
    id: str = Field(default_factory=lambda: f"meet_{uuid4().hex[:12]}")
    lead_id: str
    conversation_id: Optional[str] = None

    title: str = "Discovery & Strategy Session"
    scheduled_at: Optional[str] = None
    duration_minutes: int = 30
    timezone: str = "UTC"

    status: MeetingStatus = MeetingStatus.REQUESTED
    meeting_url: Optional[str] = None
    ics_content: Optional[str] = None

    organizer_email: Optional[str] = None
    attendee_email: Optional[str] = None

    notes: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    created_at: str = Field(default_factory=utc_now_iso)
    updated_at: str = Field(default_factory=utc_now_iso)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
