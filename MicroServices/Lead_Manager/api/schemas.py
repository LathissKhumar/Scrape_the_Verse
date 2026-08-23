"""
FastAPI Request & Response Schemas for Lead Manager.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from ..domain.stage import LeadStage, TaskStatus


class CreateLeadRequest(BaseModel):
    company_name: str
    campaign_id: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    website_url: Optional[str] = None
    primary_contact_name: Optional[str] = None
    primary_contact_email: Optional[str] = None
    primary_contact_phone: Optional[str] = None
    source: Optional[str] = "leadfinder"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class UpdateLeadRequest(BaseModel):
    company_name: Optional[str] = None
    stage: Optional[LeadStage] = None
    fit_score: Optional[float] = None
    opportunity_score: Optional[float] = None
    recommended_services: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class IngestEventRequest(BaseModel):
    type: str
    lead_id: str
    actor: Optional[str] = "system"
    payload: Dict[str, Any] = Field(default_factory=dict)


class UpdateTaskStatusRequest(BaseModel):
    status: TaskStatus
    metadata: Optional[Dict[str, Any]] = None


class ScheduleMeetingRequest(BaseModel):
    lead_id: str
    title: str = "Discovery & Strategy Call"
    scheduled_at: str
    duration_minutes: int = 30
    organizer_email: str = "sales@agencyos.local"
    attendee_email: str
    conversation_id: Optional[str] = None
    notes: Optional[str] = None
