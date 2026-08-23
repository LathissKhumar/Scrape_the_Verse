"""
Unit tests for LangGraph state machine execution.
"""

import os
import pytest
from MicroServices.Lead_Manager.domain.lead import Lead
from MicroServices.Lead_Manager.domain.stage import EmailIntent, LeadStage, TaskType
from MicroServices.Lead_Manager.orchestration.graph import get_workflow_app
from MicroServices.Lead_Manager.repository.activities import ActivityRepository
from MicroServices.Lead_Manager.repository.database import get_db_manager
from MicroServices.Lead_Manager.repository.leads import LeadRepository
from MicroServices.Lead_Manager.repository.tasks import TaskRepository

TEST_DB = ".test_graph.sqlite"


@pytest.fixture(autouse=True)
async def setup_db():
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    manager = get_db_manager(db_path=TEST_DB)
    await manager.init_db()
    yield manager
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


@pytest.mark.asyncio
async def test_workflow_qualify_and_email_intent():
    db = get_db_manager(db_path=TEST_DB)
    lead_repo = LeadRepository(db)
    task_repo = TaskRepository(db)
    act_repo = ActivityRepository(db)

    # 1. Seed Lead
    lead = Lead(
        company_name="Solomon Law Firm",
        primary_contact_name="James Solomon",
        primary_contact_email="james@solomonlaw.com",
        stage=LeadStage.DISCOVERED,
    )
    await lead_repo.create(lead)

    workflow = get_workflow_app()

    # 2. Ingest lead.qualified event
    res1 = await workflow.ainvoke(
        {
            "event_id": "evt_1",
            "event_type": "lead.qualified",
            "lead_id": lead.id,
            "actor": "SDR",
            "payload": {"reason": "Verified Google Maps listing and active phone."},
        }
    )

    lead_after_1 = await lead_repo.get_by_id(lead.id)
    assert lead_after_1.stage == LeadStage.QUALIFIED

    # Check tasks created for stage entry QUALIFIED
    tasks_1 = await task_repo.get_by_lead_id(lead.id)
    assert any(t.type == TaskType.AUDIT_WEBSITE.value for t in tasks_1)

    # 3. Simulate outreach sent
    await lead_repo.update_stage(lead.id, LeadStage.CONTACTED)

    # 4. Ingest inbound email requesting meeting
    res2 = await workflow.ainvoke(
        {
            "event_id": "evt_2",
            "event_type": "email.received",
            "lead_id": lead.id,
            "actor": "CommunicationService",
            "payload": {
                "body": "Hi, thanks for reaching out. Let's schedule a Zoom call for next Tuesday at 2 PM.",
                "intent": EmailIntent.REQUEST_MEETING.value,
                "proposed_time": "2026-08-25T14:00:00Z",
            },
        }
    )

    lead_after_2 = await lead_repo.get_by_id(lead.id)
    assert lead_after_2.stage == LeadStage.MEETING_REQUESTED

    # Check that a SCHEDULE_MEETING task was created
    tasks_2 = await task_repo.get_by_lead_id(lead.id)
    assert any(t.type == TaskType.SCHEDULE_MEETING.value for t in tasks_2)
