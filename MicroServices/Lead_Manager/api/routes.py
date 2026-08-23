"""
FastAPI Routes for Lead Manager.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from ..domain.activity import LeadActivity
from ..domain.lead import Lead
from ..domain.meeting import Meeting
from ..domain.opportunity import Opportunity
from ..domain.stage import LeadStage, MeetingStatus, TaskStatus
from ..domain.task import LeadTask
from ..events.handlers import handle_incoming_event
from ..events.publishers import EventPublisher
from ..orchestration.graph import get_workflow_app
from ..repository.activities import ActivityRepository
from ..repository.conversations import ConversationRepository
from ..repository.database import get_db_manager
from ..repository.leads import LeadRepository
from ..repository.meetings import MeetingRepository
from ..repository.opportunities import OpportunityRepository
from ..repository.tasks import TaskRepository
from .schemas import (
    CreateLeadRequest,
    IngestEventRequest,
    ScheduleMeetingRequest,
    UpdateLeadRequest,
    UpdateTaskStatusRequest,
)

router = APIRouter(prefix="/api/v1", tags=["Lead Management"])


def get_repos():
    db = get_db_manager()
    return {
        "leads": LeadRepository(db),
        "opportunities": OpportunityRepository(db),
        "activities": ActivityRepository(db),
        "tasks": TaskRepository(db),
        "conversations": ConversationRepository(db),
        "meetings": MeetingRepository(db),
    }


@router.post("/leads", response_model=Lead, status_code=status.HTTP_201_CREATED)
async def create_lead_endpoint(request: CreateLeadRequest):
    repos = get_repos()
    lead = Lead(
        campaign_id=request.campaign_id,
        company_name=request.company_name,
        industry=request.industry,
        location=request.location,
        website_url=request.website_url,
        primary_contact_name=request.primary_contact_name,
        primary_contact_email=request.primary_contact_email,
        primary_contact_phone=request.primary_contact_phone,
        source=request.source or "leadfinder",
        metadata=request.metadata,
        stage=LeadStage.DISCOVERED,
    )
    created = await repos["leads"].create(lead)

    # Trigger lead.discovered event
    workflow = get_workflow_app()
    await workflow.ainvoke(
        {
            "event_id": f"evt_disc_{created.id}",
            "event_type": "lead.discovered",
            "lead_id": created.id,
            "actor": "LeadFinder",
            "payload": {"company_name": created.company_name, "source": created.source},
            "is_new_lead": True,
        }
    )

    return created


@router.get("/leads", response_model=List[Lead])
async def list_leads_endpoint(
    stage: Optional[LeadStage] = None,
    campaign_id: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    repos = get_repos()
    return await repos["leads"].list_all(
        stage=stage, campaign_id=campaign_id, limit=limit, offset=offset
    )


@router.get("/leads/pipeline/stats")
async def get_pipeline_stats_endpoint():
    repos = get_repos()
    return await repos["leads"].get_pipeline_counts()


@router.get("/leads/{lead_id}", response_model=Lead)
async def get_lead_endpoint(lead_id: str):
    repos = get_repos()
    lead = await repos["leads"].get_by_id(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.patch("/leads/{lead_id}", response_model=Lead)
async def update_lead_endpoint(lead_id: str, request: UpdateLeadRequest):
    repos = get_repos()
    updates = request.model_dump(exclude_unset=True)
    updated = await repos["leads"].update(lead_id, updates)
    if not updated:
        raise HTTPException(status_code=404, detail="Lead not found")
    return updated


@router.post("/events")
async def ingest_event_endpoint(request: IngestEventRequest):
    repos = get_repos()
    lead = await repos["leads"].get_by_id(request.lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail=f"Lead {request.lead_id} not found")

    result = await handle_incoming_event(
        event_type=request.type,
        lead_id=request.lead_id,
        actor=request.actor or "system",
        payload=request.payload,
    )
    return {
        "status": "processed",
        "lead_id": request.lead_id,
        "event_type": request.type,
        "new_stage": result.get("new_stage"),
        "transition_valid": result.get("transition_valid", False),
        "activities_created": len(result.get("created_activities", [])),
        "tasks_created": len(result.get("created_tasks", [])),
    }


@router.get("/leads/{lead_id}/activities", response_model=List[LeadActivity])
async def get_lead_activities_endpoint(lead_id: str):
    repos = get_repos()
    return await repos["activities"].get_by_lead_id(lead_id)


@router.get("/leads/{lead_id}/tasks", response_model=List[LeadTask])
async def get_lead_tasks_endpoint(lead_id: str):
    repos = get_repos()
    return await repos["tasks"].get_by_lead_id(lead_id)


@router.patch("/tasks/{task_id}", response_model=LeadTask)
async def update_task_status_endpoint(task_id: str, request: UpdateTaskStatusRequest):
    repos = get_repos()
    updated = await repos["tasks"].update_status(
        task_id=task_id, status=request.status, metadata=request.metadata
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated


@router.get("/leads/{lead_id}/opportunities", response_model=List[Opportunity])
async def get_lead_opportunities_endpoint(lead_id: str):
    repos = get_repos()
    return await repos["opportunities"].get_by_lead_id(lead_id)


@router.post("/leads/{lead_id}/approve-proposal")
async def approve_proposal_endpoint(lead_id: str):
    repos = get_repos()
    lead = await repos["leads"].get_by_id(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    result = await handle_incoming_event(
        event_type="proposal.approved",
        lead_id=lead_id,
        actor="human",
        payload={"summary": "Proposal reviewed and approved by user."},
    )
    return await repos["leads"].get_by_id(lead_id)


@router.post("/meetings", response_model=Meeting)
async def schedule_meeting_endpoint(request: ScheduleMeetingRequest):
    from ..agents.scheduling_agent import SchedulingAgent
    agent = SchedulingAgent()
    repos = get_repos()

    meeting = await agent.create_meeting_proposal(
        lead_id=request.lead_id,
        title=request.title,
        proposed_time_iso=request.scheduled_at,
        duration_minutes=request.duration_minutes,
        organizer_email=request.organizer_email,
        attendee_email=request.attendee_email,
        conversation_id=request.conversation_id,
        notes=request.notes,
    )
    saved = await repos["meetings"].create(meeting)

    await handle_incoming_event(
        event_type="meeting.scheduled",
        lead_id=request.lead_id,
        actor="human",
        payload={"meeting_id": saved.id, "scheduled_at": saved.scheduled_at},
    )

    return saved


@router.get("/timeline/stream")
async def sse_timeline_stream():
    publisher = EventPublisher.get_instance()
    queue = publisher.subscribe()

    async def event_generator():
        try:
            while True:
                msg = await queue.get()
                yield f"data: {json.dumps(msg)}\n\n"
        except asyncio.CancelledError:
            publisher.unsubscribe(queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


# ------------------------------------------------------------------------------
# Twenty CRM On-Demand Lifecycle Management Endpoints
# ------------------------------------------------------------------------------

@router.get("/crm/status")
async def get_crm_status_endpoint():
    """Returns real-time status of the self-hosted Twenty CRM instance."""
    from ..crm.lifecycle import TwentyLifecycleManager
    mgr = TwentyLifecycleManager.get_instance()
    is_up = await mgr.is_crm_responsive()
    return {
        "crm": "twenty",
        "enabled": mgr.enabled,
        "base_url": mgr.base_url,
        "is_responsive": is_up,
        "active_leases": mgr._active_leases,
    }


@router.post("/crm/spin-up")
async def spin_up_crm_endpoint(max_wait: int = Query(default=45, ge=5, le=120)):
    """Spins up the Twenty CRM Docker containers on demand."""
    from ..crm.lifecycle import TwentyLifecycleManager
    mgr = TwentyLifecycleManager.get_instance()
    success = await mgr.spin_up(max_wait_seconds=max_wait)
    return {"success": success, "crm": "twenty", "status": "running" if success else "failed"}


@router.post("/crm/spin-down")
async def spin_down_crm_endpoint(force: bool = Query(default=False)):
    """Spins down the Twenty CRM Docker containers (all database data preserved)."""
    from ..crm.lifecycle import TwentyLifecycleManager
    mgr = TwentyLifecycleManager.get_instance()
    success = await mgr.spin_down(force=force)
    return {"success": success, "crm": "twenty", "status": "stopped" if success else "busy"}
