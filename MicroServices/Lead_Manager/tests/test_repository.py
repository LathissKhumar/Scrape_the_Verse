"""
Unit tests for async SQLite repositories.
"""

import os

import pytest

from MicroServices.Lead_Manager.domain.lead import Lead
from MicroServices.Lead_Manager.domain.opportunity import Opportunity
from MicroServices.Lead_Manager.domain.stage import LeadStage, TaskStatus, TaskType
from MicroServices.Lead_Manager.domain.task import LeadTask
from MicroServices.Lead_Manager.repository.database import DatabaseManager
from MicroServices.Lead_Manager.repository.leads import LeadRepository
from MicroServices.Lead_Manager.repository.opportunities import OpportunityRepository
from MicroServices.Lead_Manager.repository.tasks import TaskRepository

TEST_DB = ".test_repo.sqlite"


@pytest.fixture
async def db():
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    manager = DatabaseManager(db_path=TEST_DB)
    await manager.init_db()
    yield manager
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


@pytest.mark.asyncio
async def test_lead_and_task_crud(db):
    lead_repo = LeadRepository(db)
    task_repo = TaskRepository(db)
    opp_repo = OpportunityRepository(db)

    # 1. Create Lead
    lead = Lead(
        company_name="Apex Dental Care",
        primary_contact_name="Dr. Sarah Jenkins",
        primary_contact_email="sarah@apexdental.com",
        stage=LeadStage.DISCOVERED,
    )
    created_lead = await lead_repo.create(lead)
    assert created_lead.id == lead.id

    # 2. Add Opportunity
    opp = Opportunity(
        lead_id=created_lead.id,
        type="LOCAL_SEO",
        score=88.5,
        problem_summary="Missing local citation and Schema.org markup",
    )
    await opp_repo.create(opp)
    opps = await opp_repo.get_by_lead_id(created_lead.id)
    assert len(opps) == 1
    assert opps[0].type == "LOCAL_SEO"

    # 3. Create Task
    task = LeadTask(
        lead_id=created_lead.id,
        type=TaskType.AUDIT_WEBSITE.value,
        assigned_to="SDR",
        title="Execute deep SEO audit",
    )
    await task_repo.create(task)
    tasks = await task_repo.get_by_lead_id(created_lead.id)
    assert len(tasks) == 1
    assert tasks[0].status == TaskStatus.PENDING

    # 4. Update Task
    updated_task = await task_repo.update_status(tasks[0].id, TaskStatus.COMPLETED)
    assert updated_task.status == TaskStatus.COMPLETED

    # 5. Update Lead recommended_services
    updated_lead = await lead_repo.update(
        created_lead.id, {"recommended_services": ["WEBSITE_REDESIGN", "LOCAL_SEO"]}
    )
    assert updated_lead is not None
    assert len(updated_lead.recommended_services) == 2
    assert "WEBSITE_REDESIGN" in updated_lead.recommended_services
