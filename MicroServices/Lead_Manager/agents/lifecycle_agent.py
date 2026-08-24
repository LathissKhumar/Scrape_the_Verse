"""
Lifecycle Agent for Lead Manager.
Determines next actions and orchestrates multi-agent delegation.
"""

from typing import Any

from ..config.logging import get_logger
from ..domain.lead import Lead
from ..domain.stage import LeadStage
from .llm_factory import LLMClient

logger = get_logger("LifecycleAgent")


class LifecycleAgent:
    def __init__(self, llm_client: LLMClient | None = None):
        self.llm = llm_client or LLMClient()

    async def recommend_next_action(
        self, lead: Lead, context: dict[str, Any]
    ) -> dict[str, Any]:
        stage = lead.stage
        if stage in (LeadStage.DISCOVERED, LeadStage.QUALIFIED):
            return {"next_step": "AUDIT_WEBSITE", "delegated_service": "SDR"}
        elif stage == LeadStage.OPPORTUNITY_IDENTIFIED:
            return {"next_step": "GENERATE_PROPOSAL", "delegated_service": "SDR"}
        elif stage == LeadStage.PROPOSAL_READY:
            return {"next_step": "HUMAN_APPROVAL", "delegated_service": "UI"}
        elif stage == LeadStage.CONTACT_READY:
            return {
                "next_step": "SEND_EMAIL",
                "delegated_service": "CommunicationService",
            }
        elif stage == LeadStage.MEETING_REQUESTED:
            return {
                "next_step": "SCHEDULE_CALENDAR",
                "delegated_service": "SchedulingAgent",
            }
        return {"next_step": "MONITOR", "delegated_service": "LifecycleAgent"}
