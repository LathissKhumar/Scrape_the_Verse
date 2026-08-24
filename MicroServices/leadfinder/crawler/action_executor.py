"""Strict, allowlisted action plan executor for Playwright pages."""

import asyncio
import logging
from typing import Any

from leadfinder.crawler.action_models import (
    ActionPlan,
    ClickAction,
    ExtractAction,
    FillAction,
    NavigateAction,
    ScrollAction,
    SelectAction,
    SolveCaptchaAction,
    WaitForAction,
)

logger = logging.getLogger("CRAWLER_ACTION_EXECUTOR")


class ActionPlanExecutor:
    """Executes declarative ActionPlans on a Playwright Page with strict allowlist enforcement."""

    async def execute_plan(self, page: Any, plan: ActionPlan) -> dict[str, Any]:
        """Execute each action sequentially on the provided Playwright page."""
        extracted_data: dict[str, Any] = {}

        for idx, action in enumerate(plan.actions, 1):
            logger.debug(
                f"[Action {idx}/{len(plan.actions)}] Executing {action.action_type}"
            )
            if isinstance(action, NavigateAction):
                await page.goto(action.url, timeout=action.timeout_ms)
            elif isinstance(action, WaitForAction):
                if action.selector:
                    await page.wait_for_selector(
                        action.selector, state=action.state, timeout=action.timeout_ms
                    )
                else:
                    await page.wait_for_load_state(
                        "networkidle", timeout=action.timeout_ms
                    )
            elif isinstance(action, ClickAction):
                await page.click(action.selector, timeout=action.timeout_ms)
            elif isinstance(action, FillAction):
                await page.fill(action.selector, action.text, timeout=action.timeout_ms)
            elif isinstance(action, SelectAction):
                await page.select_option(
                    action.selector, action.value, timeout=action.timeout_ms
                )
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
                        logger.warning(
                            f"Failed to extract field '{field_name}' with selector '{selector}': {e}"
                        )
                        extracted_data[field_name] = None
            elif isinstance(action, SolveCaptchaAction):
                logger.info(
                    f"Executing CAPTCHA solve action (type={action.captcha_type}, timeout={action.timeout_ms}ms)..."
                )
                try:
                    solved = False
                    # 1. Custom selector if specified
                    if action.selector:
                        try:
                            elem = await page.wait_for_selector(
                                action.selector,
                                state="visible",
                                timeout=min(5000, action.timeout_ms),
                            )
                            if elem:
                                await elem.click()
                                solved = True
                        except Exception as sel_err:
                            logger.debug(
                                f"Custom CAPTCHA selector '{action.selector}' click attempt: {sel_err}"
                            )

                    # 2. Cloudflare Turnstile detection & click
                    if not solved and action.captcha_type in ("turnstile", "auto"):
                        for frame in getattr(page, "frames", []):
                            frame_url = getattr(frame, "url", "")
                            if (
                                "challenges.cloudflare.com" in frame_url
                                or "turnstile" in frame_url
                            ):
                                try:
                                    if hasattr(frame, "query_selector"):
                                        checkbox = await frame.query_selector(
                                            "input[type='checkbox'], .cb-lb, .ctp-checkbox-label, #challenge-stage"
                                        )
                                        if checkbox:
                                            await checkbox.click()
                                            solved = True
                                            break
                                    await frame.click("body")
                                    solved = True
                                    break
                                except Exception as frame_err:
                                    logger.debug(
                                        f"Turnstile iframe click error: {frame_err}"
                                    )

                    # 3. Google reCAPTCHA detection & click
                    if not solved and action.captcha_type in ("recaptcha", "auto"):
                        for frame in getattr(page, "frames", []):
                            frame_url = getattr(frame, "url", "")
                            if (
                                "google.com/recaptcha" in frame_url
                                or "recaptcha" in frame_url
                            ):
                                try:
                                    if hasattr(frame, "query_selector"):
                                        anchor = await frame.query_selector(
                                            ".recaptcha-checkbox-border, #recaptcha-anchor"
                                        )
                                        if anchor:
                                            await anchor.click()
                                            solved = True
                                            break
                                    await frame.click("body")
                                    solved = True
                                    break
                                except Exception as recap_err:
                                    logger.debug(
                                        f"reCAPTCHA anchor click error: {recap_err}"
                                    )

                    # 4. hCaptcha detection & click
                    if not solved and action.captcha_type in ("hcaptcha", "auto"):
                        for frame in getattr(page, "frames", []):
                            frame_url = getattr(frame, "url", "")
                            if "hcaptcha.com" in frame_url:
                                try:
                                    if hasattr(frame, "query_selector"):
                                        checkbox = await frame.query_selector(
                                            "#checkbox, .anchor-checkbox"
                                        )
                                        if checkbox:
                                            await checkbox.click()
                                            solved = True
                                            break
                                    await frame.click("body")
                                    solved = True
                                    break
                                except Exception as hcap_err:
                                    logger.debug(
                                        f"hCaptcha checkbox click error: {hcap_err}"
                                    )

                    if solved:
                        extracted_data["_captcha_solved"] = True
                        extracted_data["_captcha_status"] = "solved"
                        if hasattr(page, "wait_for_timeout"):
                            try:
                                await page.wait_for_timeout(1000)
                            except Exception:
                                pass
                    else:
                        extracted_data["_captcha_status"] = "skipped"
                except Exception as e:
                    logger.warning(f"Error during CAPTCHA solving hook: {e}")
                    extracted_data["_captcha_status"] = "failed"

        return extracted_data
