"""
Lead Domain Model.
"""

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from .stage import LeadStage


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class Lead(BaseModel):
    id: str = Field(default_factory=lambda: f"lead_{uuid4().hex[:12]}")
    campaign_id: str | None = None

    company_name: str
    industry: str | None = None
    location: str | None = None
    website_url: str | None = None

    primary_contact_name: str | None = None
    primary_contact_email: str | None = None
    primary_contact_phone: str | None = None

    stage: LeadStage = LeadStage.DISCOVERED

    fit_score: float | None = None
    opportunity_score: float | None = None

    recommended_services: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    source: str = "leadfinder"
    created_at: str = Field(default_factory=utc_now_iso)
    updated_at: str = Field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()
