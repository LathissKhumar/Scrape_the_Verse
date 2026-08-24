"""
LangGraph Workflow State Definition for Lead Manager.
"""

from typing import Any

from typing_extensions import TypedDict


class LeadWorkflowState(TypedDict, total=False):
    event_id: str
    event_type: str
    lead_id: str
    actor: str
    payload: dict[str, Any]

    current_stage: str
    new_stage: str | None
    lead_data: dict[str, Any] | None
    validation_error: str | None
    transition_valid: bool
    transition_reason: str | None

    intent_result: dict[str, Any] | None
    meeting_result: dict[str, Any] | None

    created_activities: list[dict[str, Any]]
    created_tasks: list[dict[str, Any]]
    published_events: list[dict[str, Any]]

    is_new_lead: bool
