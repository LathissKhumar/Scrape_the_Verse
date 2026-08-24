"""
Action & Task Generation Policy for Lead Manager.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

from ..domain.stage import EmailIntent, LeadStage, TaskType
from ..domain.task import LeadTask

INTENT_TASK_MAPPING = {
    EmailIntent.REQUEST_MEETING.value: {
        "type": TaskType.SCHEDULE_MEETING.value,
        "assigned_to": "human",
        "title": "Schedule Meeting with Prospect",
        "description": "Prospect requested a meeting. Verify suggested times and confirm calendar invite.",
    },
    EmailIntent.REQUEST_PRICING.value: {
        "type": TaskType.RESPOND_TO_PROSPECT.value,
        "assigned_to": "SDR",
        "title": "Respond to Pricing Inquiry",
        "description": "Prospect asked for pricing details. Draft tailored quote.",
    },
    EmailIntent.REQUEST_MORE_INFO.value: {
        "type": TaskType.RESPOND_TO_PROSPECT.value,
        "assigned_to": "SDR",
        "title": "Answer Prospect Information Request",
        "description": "Prospect asked questions about the audit/proposal. Provide detailed response.",
    },
    EmailIntent.INTERESTED.value: {
        "type": TaskType.FOLLOW_UP.value,
        "assigned_to": "SDR",
        "title": "Engage Interested Prospect",
        "description": "Prospect showed interest. Send next steps or propose a quick call.",
    },
    EmailIntent.NEGOTIATING.value: {
        "type": TaskType.PREPARE_NEGOTIATION.value,
        "assigned_to": "human",
        "title": "Prepare Negotiation / Custom Terms",
        "description": "Prospect entered active negotiation. Review scope, deliverables, and pricing.",
    },
    EmailIntent.OUT_OF_OFFICE.value: {
        "type": TaskType.FOLLOW_UP.value,
        "assigned_to": "system",
        "title": "Follow up after OOO period",
        "description": "Prospect is out of office. Re-engage in 5 days.",
    },
}

STAGE_ENTRY_TASKS = {
    LeadStage.DISCOVERED: {
        "type": TaskType.RESEARCH_LEAD.value,
        "assigned_to": "SDR",
        "title": "Research and Qualify Lead",
        "description": "Verify business listing, online presence, and service fit.",
    },
    LeadStage.QUALIFIED: {
        "type": TaskType.AUDIT_WEBSITE.value,
        "assigned_to": "SDR",
        "title": "Crawl & Audit Website",
        "description": "Perform SEO, performance, and UX audit to identify opportunities.",
    },
    LeadStage.OPPORTUNITY_IDENTIFIED: {
        "type": TaskType.GENERATE_PROPOSAL.value,
        "assigned_to": "SDR",
        "title": "Generate Tailored Proposal",
        "description": "Draft client-specific proposal addressing identified weaknesses.",
    },
    LeadStage.PROPOSAL_READY: {
        "type": TaskType.REVIEW_PROPOSAL.value,
        "assigned_to": "human",
        "title": "Review and Approve Proposal",
        "description": "Human review required before sending outreach to prospect.",
    },
    LeadStage.CONTACT_READY: {
        "type": TaskType.SEND_OUTREACH.value,
        "assigned_to": "CommunicationService",
        "title": "Dispatch Approved Outreach Email",
        "description": "Send proposal email via Communication Service.",
    },
    LeadStage.MEETING_REQUESTED: {
        "type": TaskType.SCHEDULE_MEETING.value,
        "assigned_to": "human",
        "title": "Confirm Meeting Schedule",
        "description": "Review prospect meeting time and confirm ICS calendar invite.",
    },
}


def get_tasks_for_intent(
    lead_id: str,
    intent: str,
    metadata: dict[str, Any] | None = None,
) -> list[LeadTask]:
    intent_norm = intent.upper() if intent else ""
    if intent_norm in INTENT_TASK_MAPPING:
        spec = INTENT_TASK_MAPPING[intent_norm]
        meta = metadata.copy() if metadata else {}
        meta["triggered_by_intent"] = intent_norm

        task = LeadTask(
            lead_id=lead_id,
            type=spec["type"],
            assigned_to=spec["assigned_to"],
            title=spec["title"],
            description=spec["description"],
            metadata=meta,
        )
        return [task]
    return []


def get_tasks_for_stage_entry(
    lead_id: str,
    new_stage: LeadStage,
    metadata: dict[str, Any] | None = None,
) -> list[LeadTask]:
    if new_stage in STAGE_ENTRY_TASKS:
        spec = STAGE_ENTRY_TASKS[new_stage]
        meta = metadata.copy() if metadata else {}
        meta["triggered_by_stage"] = new_stage.value

        task = LeadTask(
            lead_id=lead_id,
            type=spec["type"],
            assigned_to=spec["assigned_to"],
            title=spec["title"],
            description=spec["description"],
            metadata=meta,
        )
        return [task]
    return []


def evaluate_stale_lead(
    lead_dict: dict[str, Any],
    stale_days_contacted: int = 3,
    stale_days_engaged: int = 2,
    stale_days_proposal: int = 2,
) -> LeadTask | None:
    stage = lead_dict.get("stage")
    updated_at_str = lead_dict.get("updated_at") or lead_dict.get("created_at")
    lead_id = lead_dict.get("id")

    if not updated_at_str or not lead_id:
        return None

    try:
        updated_at = datetime.fromisoformat(updated_at_str)
        if updated_at.tzinfo is None:
            updated_at = updated_at.replace(tzinfo=timezone.utc)
    except Exception:
        return None

    now = datetime.now(timezone.utc)
    elapsed = now - updated_at

    threshold = None
    task_title = ""
    task_desc = ""

    if stage == LeadStage.CONTACTED.value:
        threshold = timedelta(days=stale_days_contacted)
        task_title = "Follow up on Sent Proposal"
        task_desc = f"No response received in {stale_days_contacted} days since initial outreach."
    elif stage == LeadStage.ENGAGED.value or stage == LeadStage.REQUEST_INFO.value:
        threshold = timedelta(days=stale_days_engaged)
        task_title = "Follow up with Engaged Prospect"
        task_desc = (
            f"Conversation paused for {stale_days_engaged} days. Nudge prospect."
        )
    elif stage == LeadStage.PROPOSAL_READY.value:
        threshold = timedelta(days=stale_days_proposal)
        task_title = "Pending Human Proposal Approval"
        task_desc = f"Proposal has been waiting for human approval for {stale_days_proposal} days."

    if threshold and elapsed >= threshold:
        return LeadTask(
            lead_id=lead_id,
            type=TaskType.FOLLOW_UP.value,
            assigned_to="SDR" if stage != LeadStage.PROPOSAL_READY.value else "human",
            title=task_title,
            description=task_desc,
            metadata={
                "stale_stage": stage,
                "days_elapsed": elapsed.days,
                "last_updated": updated_at_str,
            },
        )

    return None
