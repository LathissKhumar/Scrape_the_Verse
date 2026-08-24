"""
FastAPI Request & Response Schemas for Lead Manager.
"""

from typing import Any

from pydantic import BaseModel, Field

from ..domain.stage import LeadStage, TaskStatus


class CreateLeadRequest(BaseModel):
    company_name: str
    campaign_id: str | None = None
    industry: str | None = None
    location: str | None = None
    website_url: str | None = None
    primary_contact_name: str | None = None
    primary_contact_email: str | None = None
    primary_contact_phone: str | None = None
    source: str | None = "leadfinder"
    metadata: dict[str, Any] = Field(default_factory=dict)


class UpdateLeadRequest(BaseModel):
    company_name: str | None = None
    stage: LeadStage | None = None
    fit_score: float | None = None
    opportunity_score: float | None = None
    recommended_services: list[str] | None = None
    metadata: dict[str, Any] | None = None


class IngestEventRequest(BaseModel):
    type: str
    lead_id: str
    actor: str | None = "system"
    payload: dict[str, Any] = Field(default_factory=dict)


class UpdateTaskStatusRequest(BaseModel):
    status: TaskStatus
    metadata: dict[str, Any] | None = None


class ScheduleMeetingRequest(BaseModel):
    lead_id: str
    title: str = "Discovery & Strategy Call"
    scheduled_at: str
    duration_minutes: int = 30
    organizer_email: str = "sales@agencyos.local"
    attendee_email: str
    conversation_id: str | None = None
    notes: str | None = None
