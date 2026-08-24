"""
Twenty CRM Adapter for AgencyOS Lead Manager.
Bridges internal AgencyOS domain entities (Lead, Opportunity, Task, CallSession)
with open-source Twenty CRM objects.
"""

import logging
from typing import Any, Optional

from ..config.settings import get_settings
from ..domain.lead import Lead
from ..domain.opportunity import Opportunity
from ..domain.stage import LeadStage
from ..domain.task import Task
from .twenty_client import TwentyCRMClient

logger = logging.getLogger("TwentyCRMAdapter")


class TwentyCRMAdapter:
    """
    Coordinates automatic synchronization between Lead Manager workflows and Twenty CRM.
    """

    _instance: Optional["TwentyCRMAdapter"] = None

    def __init__(self, client: TwentyCRMClient | None = None):
        settings = get_settings()
        self.enabled = settings.TWENTY_CRM_ENABLED
        self.client = client or TwentyCRMClient(
            base_url=settings.TWENTY_CRM_BASE_URL,
            api_key=settings.TWENTY_CRM_API_KEY,
        )
        self._lead_company_map: dict[str, str] = {}  # lead_id -> twenty_company_id
        self._lead_person_map: dict[str, str] = {}  # lead_id -> twenty_person_id

    @classmethod
    def get_instance(cls) -> "TwentyCRMAdapter":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @staticmethod
    def map_stage_to_twenty_opportunity_stage(stage: LeadStage) -> str:
        """Maps AgencyOS LeadStage to Twenty CRM Opportunity Stages."""
        mapping = {
            LeadStage.DISCOVERED: "NEW",
            LeadStage.QUALIFIED: "SCREENING",
            LeadStage.RESEARCHED: "QUALIFIED",
            LeadStage.OPPORTUNITY_IDENTIFIED: "DISCOVERY",
            LeadStage.PROPOSAL_READY: "PROPOSAL",
            LeadStage.CONTACT_READY: "PROPOSAL",
            LeadStage.CONTACTED: "CONTACTED",
            LeadStage.ENGAGED: "ENGAGED",
            LeadStage.MEETING_REQUESTED: "MEETING_SET",
            LeadStage.MEETING_SCHEDULED: "MEETING_SET",
            LeadStage.NEGOTIATION: "NEGOTIATION",
            LeadStage.WON: "CLOSED_WON",
            LeadStage.LOST: "CLOSED_LOST",
            LeadStage.DISQUALIFIED: "CLOSED_LOST",
            LeadStage.NOT_INTERESTED: "CLOSED_LOST",
        }
        return mapping.get(stage, "NEW")

    async def sync_lead(self, lead: Lead) -> dict[str, Any]:
        """
        Synchronizes a Lead into Twenty CRM as Company + Contact Person.
        """
        if not self.enabled:
            return {"synced": False, "reason": "TWENTY_CRM_DISABLED"}

        # 1. Create / Sync Company
        company_res = await self.client.create_company(
            name=lead.company_name,
            domain_name=lead.website_url,
            address=lead.location,
            industry=lead.industry,
            metadata={"agencyos_lead_id": lead.id, "stage": lead.stage.value},
        )
        twenty_comp_id = company_res.get("id") or company_res.get(
            "createCompany", {}
        ).get("id")
        if twenty_comp_id:
            self._lead_company_map[lead.id] = twenty_comp_id

        # 2. Create / Sync Primary Contact Person
        twenty_person_id = None
        if lead.primary_contact_name:
            parts = lead.primary_contact_name.strip().split(" ", 1)
            first_name = parts[0]
            last_name = parts[1] if len(parts) > 1 else ""

            person_res = await self.client.create_person(
                first_name=first_name,
                last_name=last_name,
                email=lead.primary_contact_email,
                phone=lead.primary_contact_phone,
                company_id=twenty_comp_id,
            )
            twenty_person_id = person_res.get("id") or person_res.get(
                "createPerson", {}
            ).get("id")
            if twenty_person_id:
                self._lead_person_map[lead.id] = twenty_person_id

        return {
            "synced": True,
            "twenty_company_id": twenty_comp_id,
            "twenty_person_id": twenty_person_id,
        }

    async def sync_opportunities(
        self,
        lead_id: str,
        company_name: str,
        stage: LeadStage,
        opportunities: list[Opportunity],
    ) -> list[dict[str, Any]]:
        """
        Synchronizes AgencyOS diagnosed opportunities into Twenty CRM.
        """
        if not self.enabled or not opportunities:
            return []

        company_id = self._lead_company_map.get(lead_id)
        twenty_stage = self.map_stage_to_twenty_opportunity_stage(stage)
        synced = []

        for opp in opportunities:
            opp_name = f"{company_name} - {opp.type.replace('_', ' ').title()}"
            # Estimate offer value based on score/type
            est_value = (
                2500.0
                if "WEBSITE" in opp.type
                else (1500.0 if "SEO" in opp.type else 1000.0)
            )

            res = await self.client.create_opportunity(
                name=opp_name,
                company_id=company_id,
                amount_usd=est_value,
                stage=twenty_stage,
                point_of_contact_id=self._lead_person_map.get(lead_id),
            )
            synced.append(res)

        return synced

    async def sync_call_notes(
        self,
        lead_id: str,
        company_name: str,
        transcript: list[dict[str, Any]],
        summary: str,
        disposition: str | None = None,
        interest_score: float | None = None,
    ) -> dict[str, Any]:
        """
        Pushes Voice Agent call transcripts and disposition directly to Twenty CRM Notes.
        """
        if not self.enabled:
            return {"synced": False}

        company_id = self._lead_company_map.get(lead_id)

        # Format clean dialogue body
        dialogue_lines = []
        for t in transcript:
            speaker = t.get("speaker", "unknown").capitalize()
            text = t.get("text", "")
            dialogue_lines.append(f"**{speaker}**: {text}")
        dialogue_text = (
            "\n".join(dialogue_lines)
            if dialogue_lines
            else "No audio dialogue recorded."
        )

        note_body = (
            f"### Voice Telephony Summary\n"
            f"- **Disposition**: {disposition or 'COMPLETED'}\n"
            f"- **Interest Score**: {interest_score or 50}/100\n"
            f"- **Executive Summary**: {summary}\n\n"
            f"### Full Conversation Transcript\n"
            f"{dialogue_text}"
        )

        title = f"AI Voice Telephony Call — {company_name}"
        res = await self.client.create_note(
            title=title,
            body=note_body,
            targetable_id=company_id,
            targetable_type="company",
        )
        return res

    async def sync_task(self, lead_id: str, task: Task) -> dict[str, Any]:
        """
        Pushes AgencyOS tasks into Twenty CRM actionable Tasks.
        """
        if not self.enabled:
            return {"synced": False}

        company_id = self._lead_company_map.get(lead_id)
        res = await self.client.create_task(
            title=task.title or f"Task for {task.type}",
            body=task.description or f"Task type: {task.type}",
            status="TODO",
            due_at_iso=getattr(task, "due_at", None) or getattr(task, "due_date", None),
            targetable_id=company_id,
            targetable_type="company",
        )
        return res
