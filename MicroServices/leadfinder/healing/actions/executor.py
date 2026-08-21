"""Safe, bounded browser action executor for dynamic self-healing interaction repair."""

import asyncio
from typing import Any
from app.config.logging import get_logger
from app.healing.actions.models import ActionPlan, ActionType

logger = get_logger("ACTION_REPAIR_EXECUTOR")


class ActionRepairExecutor:
    """Executes ActionPlans on live Playwright page instances with strict safety controls."""

    async def execute_plan(self, page: Any, plan: ActionPlan) -> dict[str, Any]:
        """Safely execute up to 5 actions sequentially with bounded timeouts and error containment."""
        actions_executed: list[dict[str, Any]] = []
        logger.debug(f"Executing ActionPlan {plan.plan_id}: '{plan.description}' ({len(plan.actions)} actions)")

        # Enforce hard safety bound: maximum 5 actions per plan
        bounded_actions = plan.actions[:5]

        for idx, action in enumerate(bounded_actions, start=1):
            act_record: dict[str, Any] = {
                "step": idx,
                "action_type": action.action_type.value,
                "selector": action.selector,
                "status": "pending",
            }
            try:
                if action.action_type in (ActionType.CLICK, ActionType.ACCEPT_COOKIE, ActionType.DISMISS_OVERLAY, ActionType.CLICK_LOAD_MORE):
                    if action.selector:
                        # Safe click with timeout
                        btn = page.locator(action.selector).first
                        await btn.scroll_into_view_if_needed(timeout=action.timeout_ms)
                        await btn.click(timeout=action.timeout_ms)
                        act_record["status"] = "success"

                elif action.action_type == ActionType.SCROLL:
                    scroll_y = int(action.value or "1500")
                    await page.evaluate(f"window.scrollBy(0, {scroll_y});")
                    act_record["status"] = "success"

                elif action.action_type == ActionType.SCROLL_UNTIL:
                    if action.selector:
                        loc = page.locator(action.selector).first
                        await loc.scroll_into_view_if_needed(timeout=action.timeout_ms)
                        act_record["status"] = "success"

                elif action.action_type == ActionType.WAIT_FOR:
                    if action.selector:
                        await page.wait_for_selector(action.selector, timeout=action.timeout_ms)
                        act_record["status"] = "success"

                elif action.action_type == ActionType.WAIT_MS:
                    wait_ms = int(action.value or "1000")
                    await asyncio.sleep(min(wait_ms, 5000) / 1000.0)
                    act_record["status"] = "success"

                elif action.action_type == ActionType.HOVER:
                    if action.selector:
                        await page.hover(action.selector, timeout=action.timeout_ms)
                        act_record["status"] = "success"

            except Exception as error:
                logger.warning(f"Action step {idx} ({action.action_type.value} on {action.selector}) failed: {error}")
                act_record["status"] = "failed"
                act_record["error"] = str(error)
                if not action.optional:
                    break

            actions_executed.append(act_record)

        # Post-action stabilization pause
        if plan.wait_after_ms > 0:
            await asyncio.sleep(min(plan.wait_after_ms, 3000) / 1000.0)

        # Retrieve updated DOM content
        updated_html = ""
        try:
            updated_html = await page.content()
        except Exception:
            pass

        return {
            "plan_id": plan.plan_id,
            "description": plan.description,
            "actions_executed": actions_executed,
            "success": any(a["status"] == "success" for a in actions_executed),
            "updated_html": updated_html,
        }

