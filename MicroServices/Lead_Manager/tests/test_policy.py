"""
Unit tests for deterministic state transitions & policy actions.
"""

from MicroServices.Lead_Manager.domain.stage import EmailIntent, LeadStage, TaskType
from MicroServices.Lead_Manager.policy.actions import (
    get_tasks_for_intent,
    get_tasks_for_stage_entry,
)
from MicroServices.Lead_Manager.policy.transitions import evaluate_transition


def test_transitions_matrix():
    # DISCOVERED -> QUALIFIED
    stage, valid, _ = evaluate_transition(LeadStage.DISCOVERED, "lead.qualified")
    assert valid is True
    assert stage == LeadStage.QUALIFIED

    # QUALIFIED -> OPPORTUNITY_IDENTIFIED
    stage, valid, _ = evaluate_transition(LeadStage.QUALIFIED, "opportunity.created")
    assert valid is True
    assert stage == LeadStage.OPPORTUNITY_IDENTIFIED

    # OPPORTUNITY_IDENTIFIED -> PROPOSAL_READY
    stage, valid, _ = evaluate_transition(
        LeadStage.OPPORTUNITY_IDENTIFIED, "proposal.created"
    )
    assert valid is True
    assert stage == LeadStage.PROPOSAL_READY

    # PROPOSAL_READY -> CONTACT_READY (Human Approval)
    stage, valid, _ = evaluate_transition(LeadStage.PROPOSAL_READY, "proposal.approved")
    assert valid is True
    assert stage == LeadStage.CONTACT_READY

    # CONTACT_READY -> CONTACTED (Email Sent)
    stage, valid, _ = evaluate_transition(LeadStage.CONTACT_READY, "email.sent")
    assert valid is True
    assert stage == LeadStage.CONTACTED

    # CONTACTED -> MEETING_REQUESTED (Prospect requested meeting)
    stage, valid, _ = evaluate_transition(
        LeadStage.CONTACTED,
        "email.intent_detected",
        intent=EmailIntent.REQUEST_MEETING.value,
    )
    assert valid is True
    assert stage == LeadStage.MEETING_REQUESTED

    # MEETING_REQUESTED -> MEETING_SCHEDULED
    stage, valid, _ = evaluate_transition(
        LeadStage.MEETING_REQUESTED, "meeting.scheduled"
    )
    assert valid is True
    assert stage == LeadStage.MEETING_SCHEDULED


def test_task_generation_for_intent():
    tasks = get_tasks_for_intent("lead_123", EmailIntent.REQUEST_MEETING.value)
    assert len(tasks) == 1
    assert tasks[0].type == TaskType.SCHEDULE_MEETING.value
    assert tasks[0].assigned_to == "human"


def test_task_generation_for_stage_entry():
    tasks = get_tasks_for_stage_entry("lead_123", LeadStage.PROPOSAL_READY)
    assert len(tasks) == 1
    assert tasks[0].type == TaskType.REVIEW_PROPOSAL.value
    assert tasks[0].assigned_to == "human"
