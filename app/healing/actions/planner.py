"""Planner for generating bounded ActionPlan candidates to unblock UI interactions and lazy hydration."""

from typing import Any, Optional
from app.config.logging import get_logger
from app.healing.actions.detector import ActionIssueDetector
from app.healing.actions.models import ActionPlan, ActionType, PageAction
from app.llm.base import LLMClient
from app.models.schemas import ScrapingTask

logger = get_logger("ACTION_REPAIR_PLANNER")


class ActionRepairPlanner:
    """Synthesizes deterministic and LLM-assisted ActionPlans to resolve page interaction blocks."""

    def __init__(
        self,
        detector: Optional[ActionIssueDetector] = None,
        llm_client: Optional[LLMClient] = None,
    ):
        self.detector = detector or ActionIssueDetector()
        self.llm_client = llm_client

    def plan_from_issues(self, issues: list[dict[str, Any]], task: ScrapingTask) -> list[ActionPlan]:
        """Convert detected UI issues into ordered ActionPlan candidates."""
        candidates: list[ActionPlan] = []

        for issue in issues:
            act_type = issue.get("recommended_action", ActionType.CLICK)
            selector = issue.get("target_selector")
            val = issue.get("value")
            desc = issue.get("issue_type", "UI interaction repair")

            if act_type == ActionType.ACCEPT_COOKIE and selector:
                plan = ActionPlan(
                    description="Dismiss cookie consent banner",
                    actions=[
                        PageAction(action_type=ActionType.CLICK, selector=selector, timeout_ms=3000, description="Click accept cookies"),
                        PageAction(action_type=ActionType.WAIT_MS, value="800", description="Wait for banner dismissal"),
                    ],
                )
                candidates.append(plan)

            elif act_type == ActionType.DISMISS_OVERLAY and selector:
                plan = ActionPlan(
                    description="Dismiss blocking modal overlay",
                    actions=[
                        PageAction(action_type=ActionType.CLICK, selector=selector, timeout_ms=3000, description="Close overlay"),
                        PageAction(action_type=ActionType.WAIT_MS, value="800", description="Stabilize DOM"),
                    ],
                )
                candidates.append(plan)

            elif act_type == ActionType.CLICK_LOAD_MORE and selector:
                plan = ActionPlan(
                    description="Click Load More button to fetch additional items",
                    actions=[
                        PageAction(action_type=ActionType.SCROLL, value="1000", description="Scroll to button"),
                        PageAction(action_type=ActionType.CLICK, selector=selector, timeout_ms=4000, description="Click load more"),
                        PageAction(action_type=ActionType.WAIT_MS, value="1500", description="Wait for AJAX response"),
                    ],
                )
                candidates.append(plan)

            elif act_type == ActionType.SCROLL:
                plan = ActionPlan(
                    description="Trigger infinite scroll to hydrate dynamic items",
                    actions=[
                        PageAction(action_type=ActionType.SCROLL, value="2500", description="Scroll down page"),
                        PageAction(action_type=ActionType.WAIT_MS, value="1200", description="Wait for lazy render"),
                    ],
                )
                candidates.append(plan)

        # Fallback general scroll + wait plan if no specific issues were isolated
        if not candidates:
            candidates.append(
                ActionPlan(
                    description="General scroll down and DOM stabilization",
                    actions=[
                        PageAction(action_type=ActionType.SCROLL, value="2000", description="Scroll down"),
                        PageAction(action_type=ActionType.WAIT_MS, value="1000", description="Wait for hydration"),
                    ],
                )
            )

        return candidates
