"""
Opportunity Domain Model.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4
from pydantic import BaseModel, Field


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class Opportunity(BaseModel):
    id: str = Field(default_factory=lambda: f"opp_{uuid4().hex[:12]}")
    lead_id: str

    type: str
    score: float = 0.0

    problem_summary: Optional[str] = None
    evidence: List[Dict[str, Any]] = Field(default_factory=list)

    recommended: bool = True
    status: str = "IDENTIFIED"

    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(default_factory=utc_now_iso)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
