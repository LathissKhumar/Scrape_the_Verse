"""
Event Handlers for Lead Manager.
"""

from typing import Any

from ..config.logging import get_logger
from ..orchestration.graph import get_workflow_app

logger = get_logger("EventHandler")


async def handle_incoming_event(
    event_type: str,
    lead_id: str,
    actor: str = "system",
    payload: dict[str, Any] = None,
) -> dict[str, Any]:
    workflow = get_workflow_app()
    state = {
        "event_id": f"evt_{lead_id}",
        "event_type": event_type,
        "lead_id": lead_id,
        "actor": actor,
        "payload": payload or {},
    }

    result = await workflow.ainvoke(state)
    return result
