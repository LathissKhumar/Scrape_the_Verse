"""
Deterministic Transition Policy for Lead Manager.
"""

from typing import Optional, Tuple
from ..config.logging import get_logger
from ..domain.stage import LeadStage

logger = get_logger("PolicyEngine")

TRANSITIONS = {
    # Discovery -> Qualified / Disqualified / Researched / Opportunity
    (LeadStage.DISCOVERED, "lead.qualified"): LeadStage.QUALIFIED,
    (LeadStage.DISCOVERED, "lead.disqualified"): LeadStage.DISQUALIFIED,
    (LeadStage.DISCOVERED, "lead.researched"): LeadStage.RESEARCHED,
    (LeadStage.DISCOVERED, "lead.opportunity_identified"): LeadStage.OPPORTUNITY_IDENTIFIED,
    (LeadStage.DISCOVERED, "opportunity.created"): LeadStage.OPPORTUNITY_IDENTIFIED,

    # Qualified -> Researched / Opportunity Identified
    (LeadStage.QUALIFIED, "lead.researched"): LeadStage.RESEARCHED,
    (LeadStage.QUALIFIED, "lead.opportunity_identified"): LeadStage.OPPORTUNITY_IDENTIFIED,
    (LeadStage.QUALIFIED, "opportunity.created"): LeadStage.OPPORTUNITY_IDENTIFIED,
    (LeadStage.QUALIFIED, "lead.disqualified"): LeadStage.DISQUALIFIED,

    # Researched -> Opportunity Identified / Proposal Ready
    (LeadStage.RESEARCHED, "lead.opportunity_identified"): LeadStage.OPPORTUNITY_IDENTIFIED,
    (LeadStage.RESEARCHED, "opportunity.created"): LeadStage.OPPORTUNITY_IDENTIFIED,
    (LeadStage.RESEARCHED, "proposal.created"): LeadStage.PROPOSAL_READY,
    (LeadStage.RESEARCHED, "proposal.generated"): LeadStage.PROPOSAL_READY,

    # Opportunity Identified -> Proposal Ready
    (LeadStage.OPPORTUNITY_IDENTIFIED, "proposal.created"): LeadStage.PROPOSAL_READY,
    (LeadStage.OPPORTUNITY_IDENTIFIED, "proposal.generated"): LeadStage.PROPOSAL_READY,

    # Proposal Ready -> Contact Ready (Human Approval) / Opportunity Identified (Rejection)
    (LeadStage.PROPOSAL_READY, "proposal.approved"): LeadStage.CONTACT_READY,
    (LeadStage.PROPOSAL_READY, "proposal.rejected"): LeadStage.OPPORTUNITY_IDENTIFIED,

    # Contact Ready -> Contacted (Email sent) / Direct Meeting
    (LeadStage.CONTACT_READY, "email.sent"): LeadStage.CONTACTED,
    (LeadStage.CONTACT_READY, "meeting.scheduled"): LeadStage.MEETING_SCHEDULED,

    # Contacted -> Engaged / Meeting / Info / Disinterested
    (LeadStage.CONTACTED, "email.intent_detected:INTERESTED"): LeadStage.ENGAGED,
    (LeadStage.CONTACTED, "email.intent_detected:REQUEST_PRICING"): LeadStage.ENGAGED,
    (LeadStage.CONTACTED, "email.intent_detected:REQUEST_MORE_INFO"): LeadStage.REQUEST_INFO,
    (LeadStage.CONTACTED, "email.intent_detected:REQUEST_MEETING"): LeadStage.MEETING_REQUESTED,
    (LeadStage.CONTACTED, "email.intent_detected:NOT_INTERESTED"): LeadStage.NOT_INTERESTED,
    (LeadStage.CONTACTED, "email.intent_detected:UNSUBSCRIBE"): LeadStage.NOT_INTERESTED,
    (LeadStage.CONTACTED, "email.intent_detected:BOUNCE"): LeadStage.DISQUALIFIED,
    (LeadStage.CONTACTED, "meeting.scheduled"): LeadStage.MEETING_SCHEDULED,

    # Engaged -> Meeting / Negotiation / Disinterested
    (LeadStage.ENGAGED, "email.intent_detected:REQUEST_MEETING"): LeadStage.MEETING_REQUESTED,
    (LeadStage.ENGAGED, "email.intent_detected:NEGOTIATING"): LeadStage.NEGOTIATION,
    (LeadStage.ENGAGED, "email.intent_detected:NOT_INTERESTED"): LeadStage.NOT_INTERESTED,
    (LeadStage.ENGAGED, "email.intent_detected:REQUEST_MORE_INFO"): LeadStage.REQUEST_INFO,
    (LeadStage.ENGAGED, "meeting.scheduled"): LeadStage.MEETING_SCHEDULED,

    # Request Info -> Contacted / Meeting
    (LeadStage.REQUEST_INFO, "email.sent"): LeadStage.ENGAGED,
    (LeadStage.REQUEST_INFO, "email.intent_detected:REQUEST_MEETING"): LeadStage.MEETING_REQUESTED,
    (LeadStage.REQUEST_INFO, "meeting.scheduled"): LeadStage.MEETING_SCHEDULED,

    # Meeting Requested -> Meeting Scheduled
    (LeadStage.MEETING_REQUESTED, "meeting.scheduled"): LeadStage.MEETING_SCHEDULED,
    (LeadStage.MEETING_REQUESTED, "meeting.cancelled"): LeadStage.ENGAGED,

    # Meeting Scheduled -> Negotiation / Completed
    (LeadStage.MEETING_SCHEDULED, "meeting.completed"): LeadStage.NEGOTIATION,
    (LeadStage.MEETING_SCHEDULED, "meeting.cancelled"): LeadStage.ENGAGED,

    # Negotiation -> Won / Lost
    (LeadStage.NEGOTIATION, "deal.won"): LeadStage.WON,
    (LeadStage.NEGOTIATION, "deal.lost"): LeadStage.LOST,
}


def evaluate_transition(
    current_stage: LeadStage,
    event_type: str,
    intent: Optional[str] = None,
) -> Tuple[Optional[LeadStage], bool, str]:
    if isinstance(current_stage, str):
        try:
            current_stage = LeadStage(current_stage)
        except ValueError:
            current_stage = LeadStage.DISCOVERED

    if event_type == "lead.disqualified":
        return LeadStage.DISQUALIFIED, True, "Manually or automatically disqualified"

    keys_to_check = []
    if intent:
        intent_up = intent.upper()
        keys_to_check.append(f"email.intent_detected:{intent_up}")
        keys_to_check.append(f"email.received:{intent_up}")
        keys_to_check.append(f"{event_type}:{intent_up}")
    keys_to_check.append(event_type)

    for key in keys_to_check:
        lookup_pair = (current_stage, key)
        if lookup_pair in TRANSITIONS:
            new_stage = TRANSITIONS[lookup_pair]
            return new_stage, True, f"Transition from {current_stage.value} to {new_stage.value} via '{key}'"

    return None, False, f"No transition defined for stage '{current_stage.value}' on event '{event_type}' (intent: {intent})"
