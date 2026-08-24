"""
A2A Skills execution handler for Lead Manager.
"""

from typing import Any

from ..domain.lead import Lead
from ..domain.stage import LeadStage
from ..events.handlers import handle_incoming_event
from ..repository.database import get_db_manager
from ..repository.leads import LeadRepository


class A2ASkillsHandler:
    @staticmethod
    async def create_lead(params: dict[str, Any]) -> dict[str, Any]:
        db = get_db_manager()
        repo = LeadRepository(db)
        lead = Lead(
            company_name=params.get("company_name", "Unknown Business"),
            website_url=params.get("website_url"),
            primary_contact_name=params.get("primary_contact_name"),
            primary_contact_email=params.get("primary_contact_email"),
            industry=params.get("industry"),
            location=params.get("location"),
            source=params.get("source", "a2a"),
            stage=LeadStage.DISCOVERED,
        )
        saved = await repo.create(lead)
        return saved.to_dict()

    @staticmethod
    async def ingest_event(params: dict[str, Any]) -> dict[str, Any]:
        event_type = params.get("event_type")
        lead_id = params.get("lead_id")
        actor = params.get("actor", "a2a_caller")
        payload = params.get("payload", {})

        result = await handle_incoming_event(
            event_type=event_type,
            lead_id=lead_id,
            actor=actor,
            payload=payload,
        )
        return result

    @staticmethod
    async def get_lead_status(params: dict[str, Any]) -> dict[str, Any]:
        db = get_db_manager()
        repo = LeadRepository(db)
        lead_id = params.get("lead_id")
        email = params.get("email")

        if lead_id:
            lead = await repo.get_by_id(lead_id)
        elif email:
            lead = await repo.get_by_email(email)
        else:
            return {"error": "lead_id or email must be provided."}

        return lead.to_dict() if lead else {"error": "Lead not found."}
