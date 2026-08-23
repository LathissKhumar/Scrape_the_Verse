"""
Call Session Domain Models for Voice Agent (Layer 9).
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4
from pydantic import BaseModel, Field


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class CallStatus(str, Enum):
    INITIATED = "INITIATED"
    RINGING = "RINGING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    NO_ANSWER = "NO_ANSWER"
    BUSY = "BUSY"


class CallDisposition(str, Enum):
    MEETING_BOOKED = "MEETING_BOOKED"
    INTERESTED = "INTERESTED"
    REQUESTED_INFO = "REQUESTED_INFO"
    NOT_INTERESTED = "NOT_INTERESTED"
    CALL_BACK_LATER = "CALL_BACK_LATER"
    WRONG_NUMBER = "WRONG_NUMBER"
    DISQUALIFIED = "DISQUALIFIED"


class CallTurn(BaseModel):
    speaker: str  # "agent" or "prospect"
    text: str
    timestamp: str = Field(default_factory=utc_now_iso)
    intent_detected: Optional[str] = None


class CallSession(BaseModel):
    id: str = Field(default_factory=lambda: f"call_{uuid4().hex[:12]}")
    lead_id: Optional[str] = None
    company_name: str
    prospect_phone: Optional[str] = None
    contact_name: Optional[str] = None

    status: CallStatus = CallStatus.INITIATED
    disposition: Optional[CallDisposition] = None
    interest_score: float = 0.0  # 0 to 100

    transcript: List[CallTurn] = Field(default_factory=list)
    call_summary: Optional[str] = None
    booked_meeting_time: Optional[str] = None

    duration_seconds: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(default_factory=utc_now_iso)
    updated_at: str = Field(default_factory=utc_now_iso)
