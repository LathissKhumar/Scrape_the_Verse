"""Strict, allowlisted action plan executor for Playwright pages."""

import asyncio
import logging
from typing import Any, Dict, Optional
from app.crawler.action_models import (
    ActionPlan,
    ClickAction,
    ExtractAction,
    FillAction,
    NavigateAction,
    ScrollAction,
    SelectAction,
    WaitForAction,
)

logger = logging.getLogger("CRAWLER_ACTION_EXECUTOR")


class ActionPlanExecutor:
    """Executes declarative ActionPlans on a Playwright Page with strict allowlist enforcement."""

    async def execute_plan(self, page: Any, plan: ActionPlan) -> Dict[str, Any]:
        """Execute each action sequentially on the provided Playwright page."""
        extracted_data: Dict[str, Any] = {}

        for idx, action in enumerate(plan.actions, 1):
            logger.debug(f"[Action {idx}/{len(plan.actions)}] Executing {action.action_type}")
            if isinstance(action, NavigateAction):
                await page.goto(action.url, timeout=action.timeout_ms)
            elif isinstance(action, WaitForAction):
                if action.selector:
                    await page.wait_for_selector(action.selector, state=action.state, timeout=action.timeout_ms)
                else:
                    await page.wait_for_load_state("networkidle", timeout=action.timeout_ms)
            elif isinstance(action, ClickAction):
                await page.click(action.selector, timeout=action.timeout_ms)
            elif isinstance(action, FillAction):
                await page.fill(action.selector, action.text, timeout=action.timeout_ms)
            elif isinstance(action, SelectAction):
                await page.select_option(action.selector, action.value, timeout=action.timeout_ms)
            elif isinstance(action, ScrollAction):
                for _ in range(action.max_iterations):
                    await page.evaluate(f"window.scrollBy(0, {action.distance_px});")
                    await asyncio.sleep(action.delay_ms / 1000.0)
            elif isinstance(action, ExtractAction):
                for field_name, selector in action.fields.items():
                    try:
                        elem = await page.query_selector(selector)
                        if elem:
                            text = await elem.inner_text()
                            extracted_data[field_name] = text.strip()
                        else:
                            extracted_data[field_name] = None
                    except Exception as e:
                        logger.warning(f"Failed to extract field '{field_name}' with selector '{selector}': {e}")
                        extracted_data[field_name] = None

        return extracted_data
