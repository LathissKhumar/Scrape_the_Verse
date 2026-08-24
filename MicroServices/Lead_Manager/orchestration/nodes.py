"""
LangGraph Workflow Nodes for Lead Manager.
"""

from typing import Any

from ..agents.conversation_agent import ConversationAgent
from ..agents.scheduling_agent import SchedulingAgent
from ..config.logging import get_logger
from ..domain.activity import LeadActivity
from ..domain.opportunity import Opportunity
from ..domain.stage import ActivityType, EmailIntent, LeadStage
from ..policy.actions import get_tasks_for_intent, get_tasks_for_stage_entry
from ..policy.transitions import evaluate_transition
from ..repository.activities import ActivityRepository
from ..repository.conversations import ConversationRepository
from ..repository.database import get_db_manager
from ..repository.leads import LeadRepository
from ..repository.meetings import MeetingRepository
from ..repository.opportunities import OpportunityRepository
from ..repository.tasks import TaskRepository
from .state import LeadWorkflowState

logger = get_logger("WorkflowNodes")


async def load_lead_state_node(state: LeadWorkflowState) -> dict[str, Any]:
    lead_id = state["lead_id"]
    db = get_db_manager()
    lead_repo = LeadRepository(db)

    lead = await lead_repo.get_by_id(lead_id)
    if not lead:
        return {"validation_error": f"Lead with ID {lead_id} not found."}

    return {
        "current_stage": lead.stage.value
        if hasattr(lead.stage, "value")
        else str(lead.stage),
        "lead_data": lead.to_dict(),
    }


async def validate_event_node(state: LeadWorkflowState) -> dict[str, Any]:
    if state.get("validation_error"):
        return state

    event_type = state["event_type"]
    if not event_type:
        return {"validation_error": "Event type cannot be empty."}

    return {"validation_error": None}


async def evaluate_transition_node(state: LeadWorkflowState) -> dict[str, Any]:
    if state.get("validation_error"):
        return state

    current_stage = state["current_stage"]
    event_type = state["event_type"]
    payload = state.get("payload", {})
    intent_res = state.get("intent_result") or {}
    intent = intent_res.get("intent") or payload.get("intent")

    new_stage, valid, reason = evaluate_transition(
        current_stage=LeadStage(current_stage),
        event_type=event_type,
        intent=intent,
    )

    return {
        "new_stage": new_stage.value if new_stage else None,
        "transition_valid": valid,
        "transition_reason": reason,
    }


async def execute_agents_node(state: LeadWorkflowState) -> dict[str, Any]:
    if state.get("validation_error"):
        return state

    event_type = state["event_type"]
    payload = state.get("payload", {})
    lead_data = state.get("lead_data", {})
    lead_id = state["lead_id"]

    intent_res = None
    meeting_res = None

    if event_type == "email.received":
        conv_agent = ConversationAgent()
        body = payload.get("body", "")
        intent_res = await conv_agent.analyze_message(
            lead_name=lead_data.get("primary_contact_name", "Valued Lead"),
            company_name=lead_data.get("company_name", "Prospect"),
            message_body=body,
            current_intent=payload.get("intent"),
        )

        db = get_db_manager()
        conv_repo = ConversationRepository(db)
        thread_id = payload.get("thread_id", f"th_{lead_id}")
        await conv_repo.create_or_update(
            lead_id=lead_id,
            thread_id=thread_id,
            channel="email",
            last_intent=intent_res.get("intent"),
            metadata=payload,
        )

    if state.get("new_stage") == LeadStage.MEETING_REQUESTED.value or (
        intent_res and intent_res.get("intent") == EmailIntent.REQUEST_MEETING.value
    ):
        sched_agent = SchedulingAgent()
        proposed_time = (
            payload.get("proposed_time")
            or payload.get("scheduled_at")
            or "2026-08-25T14:00:00Z"
        )
        meeting_obj = await sched_agent.create_meeting_proposal(
            lead_id=lead_id,
            title=f"Discovery Call with {lead_data.get('company_name', 'Prospect')}",
            proposed_time_iso=proposed_time,
            duration_minutes=payload.get("duration_minutes", 30),
            organizer_email="sales@agencyos.local",
            attendee_email=lead_data.get(
                "primary_contact_email", "prospect@client.com"
            ),
            notes=payload.get("notes"),
        )
        db = get_db_manager()
        meet_repo = MeetingRepository(db)
        await meet_repo.create(meeting_obj)
        meeting_res = meeting_obj.to_dict()

    return {
        "intent_result": intent_res,
        "meeting_result": meeting_res,
    }


async def update_lead_state_node(state: LeadWorkflowState) -> dict[str, Any]:
    if state.get("validation_error"):
        return state

    db = get_db_manager()
    lead_repo = LeadRepository(db)
    opp_repo = OpportunityRepository(db)
    lead_id = state["lead_id"]
    new_stage = state.get("new_stage")
    payload = state.get("payload", {})

    opp_objs = []
    if "opportunities" in payload and isinstance(payload["opportunities"], list):
        for o in payload["opportunities"]:
            opp_objs.append(
                Opportunity(
                    lead_id=lead_id,
                    type=o.get("type", "CUSTOM"),
                    score=o.get("score", 0.0),
                    problem_summary=o.get("problem_summary"),
                    evidence=o.get("evidence", []),
                    recommended=o.get("recommended", True),
                )
            )
        await opp_repo.bulk_create(opp_objs)
        rec_services = [o.type for o in opp_objs if o.recommended]
        if rec_services:
            await lead_repo.update(lead_id, {"recommended_services": rec_services})

    if new_stage:
        await lead_repo.update_stage(lead_id, LeadStage(new_stage))

    if payload.get("recommended_services"):
        await lead_repo.update(
            lead_id, {"recommended_services": payload["recommended_services"]}
        )

    updated_lead = await lead_repo.get_by_id(lead_id)

    # Synchronize with Twenty CRM
    try:
        from ..crm.twenty_adapter import TwentyCRMAdapter

        twenty_adapter = TwentyCRMAdapter.get_instance()
        if updated_lead:
            await twenty_adapter.sync_lead(updated_lead)
            if opp_objs:
                await twenty_adapter.sync_opportunities(
                    lead_id=lead_id,
                    company_name=updated_lead.company_name,
                    stage=updated_lead.stage,
                    opportunities=opp_objs,
                )
    except Exception as e:
        logger.warning(f"Twenty CRM sync in update_lead_state_node: {e}")

    return {"lead_data": updated_lead.to_dict() if updated_lead else None}


async def create_activity_and_tasks_node(state: LeadWorkflowState) -> dict[str, Any]:
    if state.get("validation_error"):
        return state

    db = get_db_manager()
    act_repo = ActivityRepository(db)
    task_repo = TaskRepository(db)

    lead_id = state["lead_id"]
    event_type = state["event_type"]
    actor = state.get("actor", "system")
    payload = state.get("payload", {})
    new_stage = state.get("new_stage")
    intent_res = state.get("intent_result")

    created_activities = []
    created_tasks = []

    act = LeadActivity(
        lead_id=lead_id,
        type=event_type,
        actor=actor,
        summary=payload.get("summary") or f"Processed event {event_type}",
        metadata=payload,
    )
    saved_act = await act_repo.create(act)
    created_activities.append(saved_act.to_dict())

    if new_stage and new_stage != state.get("current_stage"):
        stage_act = LeadActivity(
            lead_id=lead_id,
            type=ActivityType.STAGE_CHANGED.value,
            actor=actor,
            summary=f"Stage updated to {new_stage}",
            metadata={"from_stage": state.get("current_stage"), "to_stage": new_stage},
        )
        saved_stage_act = await act_repo.create(stage_act)
        created_activities.append(saved_stage_act.to_dict())

    new_task_objs = []
    if intent_res and "intent" in intent_res:
        intent_tasks = get_tasks_for_intent(
            lead_id=lead_id, intent=intent_res["intent"], metadata=intent_res
        )
        for t in intent_tasks:
            saved_t = await task_repo.create(t)
            created_tasks.append(saved_t.to_dict())
            new_task_objs.append(t)

    target_stage = (
        LeadStage(new_stage)
        if new_stage
        else (
            LeadStage(state.get("current_stage")) if state.get("is_new_lead") else None
        )
    )

    if target_stage:
        stage_tasks = get_tasks_for_stage_entry(
            lead_id=lead_id, new_stage=target_stage, metadata=payload
        )
        for t in stage_tasks:
            saved_t = await task_repo.create(t)
            created_tasks.append(saved_t.to_dict())
            new_task_objs.append(t)

    # Synchronize Notes (Call Transcripts) & Tasks with Twenty CRM
    try:
        from ..crm.twenty_adapter import TwentyCRMAdapter

        twenty_adapter = TwentyCRMAdapter.get_instance()
        lead_data = state.get("lead_data", {})
        company_name = lead_data.get("company_name", "Prospect")

        # Sync voice call transcript note if present in payload
        if payload.get("transcript") and isinstance(payload["transcript"], list):
            await twenty_adapter.sync_call_notes(
                lead_id=lead_id,
                company_name=company_name,
                transcript=payload["transcript"],
                summary=payload.get("summary", "Voice call completed."),
                disposition=payload.get("disposition"),
                interest_score=payload.get("interest_score"),
            )

        # Sync created tasks to Twenty CRM
        for t in new_task_objs:
            await twenty_adapter.sync_task(lead_id=lead_id, task=t)
    except Exception as e:
        logger.warning(f"Twenty CRM sync in create_activity_and_tasks_node: {e}")

    return {
        "created_activities": created_activities,
        "created_tasks": created_tasks,
    }


async def publish_events_node(state: LeadWorkflowState) -> dict[str, Any]:
    if state.get("validation_error"):
        return state

    from ..events.publishers import EventPublisher

    publisher = EventPublisher.get_instance()
    lead_id = state["lead_id"]

    for act in state.get("created_activities", []):
        await publisher.publish(
            f"lead.{lead_id}.activity",
            {"lead_id": lead_id, "activity": act},
        )

    return {"published_events": state.get("created_activities", [])}
