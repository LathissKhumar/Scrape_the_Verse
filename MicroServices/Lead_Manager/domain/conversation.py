"""
Conversation Domain Model.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import uuid4
from pydantic import BaseModel, Field


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class Conversation(BaseModel):
    id: str = Field(default_factory=lambda: f"conv_{uuid4().hex[:12]}")
    lead_id: str
    thread_id: str

    channel: str = "email"
    status: str = "ACTIVE"

    last_intent: Optional[str] = None
    last_message_at: Optional[str] = None
    message_count: int = 0

    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(default_factory=utc_now_iso)
    updated_at: str = Field(default_factory=utc_now_iso)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
