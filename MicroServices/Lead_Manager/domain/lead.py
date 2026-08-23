"""
Lead Domain Model.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4
from pydantic import BaseModel, Field
from .stage import LeadStage


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class Lead(BaseModel):
    id: str = Field(default_factory=lambda: f"lead_{uuid4().hex[:12]}")
    campaign_id: Optional[str] = None

    company_name: str
    industry: Optional[str] = None
    location: Optional[str] = None
    website_url: Optional[str] = None

    primary_contact_name: Optional[str] = None
    primary_contact_email: Optional[str] = None
    primary_contact_phone: Optional[str] = None

    stage: LeadStage = LeadStage.DISCOVERED

    fit_score: Optional[float] = None
    opportunity_score: Optional[float] = None

    recommended_services: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    source: str = "leadfinder"
    created_at: str = Field(default_factory=utc_now_iso)
    updated_at: str = Field(default_factory=utc_now_iso)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
