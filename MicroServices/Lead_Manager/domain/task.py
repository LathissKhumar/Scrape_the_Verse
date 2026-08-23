"""
Task Domain Model.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import uuid4
from pydantic import BaseModel, Field
from .stage import TaskStatus, TaskType


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class LeadTask(BaseModel):
    id: str = Field(default_factory=lambda: f"task_{uuid4().hex[:12]}")
    lead_id: str

    type: str
    status: TaskStatus = TaskStatus.PENDING

    due_at: Optional[str] = None
    assigned_to: str = "system"

    title: Optional[str] = None
    description: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    created_at: str = Field(default_factory=utc_now_iso)
    updated_at: str = Field(default_factory=utc_now_iso)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


# Type alias for standard naming
Task = LeadTask
