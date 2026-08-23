"""
LangGraph Workflow State Definition for Lead Manager.
"""

from typing import Any, Dict, List, Optional
from typing_extensions import TypedDict


class LeadWorkflowState(TypedDict, total=False):
    event_id: str
    event_type: str
    lead_id: str
    actor: str
    payload: Dict[str, Any]

    current_stage: str
    new_stage: Optional[str]
    lead_data: Optional[Dict[str, Any]]
    validation_error: Optional[str]
    transition_valid: bool
    transition_reason: Optional[str]

    intent_result: Optional[Dict[str, Any]]
    meeting_result: Optional[Dict[str, Any]]

    created_activities: List[Dict[str, Any]]
    created_tasks: List[Dict[str, Any]]
    published_events: List[Dict[str, Any]]

    is_new_lead: bool
