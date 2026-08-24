"""
Activity Domain Model.
"""

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class LeadActivity(BaseModel):
    id: str = Field(default_factory=lambda: f"act_{uuid4().hex[:12]}")
    lead_id: str

    type: str
    actor: str = "system"

    summary: str
    metadata: dict[str, Any] = Field(default_factory=dict)

    created_at: str = Field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()
