"""
LangGraph Workflow Graph Construction for Lead Manager.
"""

from langgraph.graph import END, START, StateGraph

from .nodes import (
    create_activity_and_tasks_node,
    evaluate_transition_node,
    execute_agents_node,
    load_lead_state_node,
    publish_events_node,
    update_lead_state_node,
    validate_event_node,
)
from .state import LeadWorkflowState


def build_lead_workflow_graph():
    builder = StateGraph(LeadWorkflowState)

    builder.add_node("load_lead_state", load_lead_state_node)
    builder.add_node("validate_event", validate_event_node)
    builder.add_node("evaluate_transition", evaluate_transition_node)
    builder.add_node("execute_agents", execute_agents_node)
    builder.add_node("update_lead_state", update_lead_state_node)
    builder.add_node("create_activity_and_tasks", create_activity_and_tasks_node)
    builder.add_node("publish_events", publish_events_node)

    builder.add_edge(START, "load_lead_state")
    builder.add_edge("load_lead_state", "validate_event")
    builder.add_edge("validate_event", "execute_agents")
    builder.add_edge("execute_agents", "evaluate_transition")
    builder.add_edge("evaluate_transition", "update_lead_state")
    builder.add_edge("update_lead_state", "create_activity_and_tasks")
    builder.add_edge("create_activity_and_tasks", "publish_events")
    builder.add_edge("publish_events", END)

    return builder.compile()


_workflow_app = None


def get_workflow_app():
    global _workflow_app
    if _workflow_app is None:
        _workflow_app = build_lead_workflow_graph()
    return _workflow_app
