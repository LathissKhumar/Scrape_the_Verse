"""
FollowUp Agent for Lead Manager.
Scans for stale leads and generates follow-up tasks.
"""

from ..config.logging import get_logger
from ..config.settings import Settings, get_settings
from ..domain.task import LeadTask
from ..policy.actions import evaluate_stale_lead
from ..repository.leads import LeadRepository
from ..repository.tasks import TaskRepository

logger = get_logger("FollowUpAgent")


class FollowUpAgent:
    def __init__(
        self,
        lead_repo: LeadRepository,
        task_repo: TaskRepository,
        settings: Settings | None = None,
    ):
        self.lead_repo = lead_repo
        self.task_repo = task_repo
        self.settings = settings or get_settings()

    async def scan_and_generate_followup_tasks(self) -> list[LeadTask]:
        all_leads = await self.lead_repo.list_all(limit=1000)
        generated_tasks: list[LeadTask] = []

        for lead in all_leads:
            lead_dict = lead.to_dict()
            stale_task = evaluate_stale_lead(
                lead_dict=lead_dict,
                stale_days_contacted=self.settings.STALE_LEAD_DAYS_CONTACTED,
                stale_days_engaged=self.settings.STALE_LEAD_DAYS_ENGAGED,
                stale_days_proposal=self.settings.STALE_LEAD_DAYS_PROPOSAL_READY,
            )
            if stale_task:
                existing_tasks = await self.task_repo.get_by_lead_id(lead.id)
                has_active = any(
                    t.type == stale_task.type
                    and t.status.value in ("PENDING", "IN_PROGRESS")
                    for t in existing_tasks
                )
                if not has_active:
                    created = await self.task_repo.create(stale_task)
                    generated_tasks.append(created)
                    logger.info(
                        f"Generated follow-up task {created.id} for lead {lead.id}"
                    )

        return generated_tasks
