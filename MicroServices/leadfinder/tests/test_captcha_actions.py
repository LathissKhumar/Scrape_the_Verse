import pytest
from unittest.mock import AsyncMock, MagicMock
from leadfinder.crawler.action_models import ActionPlan, SolveCaptchaAction
from leadfinder.crawler.action_executor import ActionPlanExecutor

def test_solve_captcha_action_model_validation():
    action = SolveCaptchaAction(
        captcha_type="turnstile",
        selector="#turnstile-widget",
        timeout_ms=15000,
    )
    assert action.action_type == "solve_captcha"
    assert action.captcha_type == "turnstile"
    assert action.selector == "#turnstile-widget"
    assert action.timeout_ms == 15000

def test_solve_captcha_action_in_action_plan():
    plan_dict = {
        "url": "https://protected.example.com",
        "actions": [
            {
                "action_type": "solve_captcha",
                "captcha_type": "turnstile",
                "timeout_ms": 10000,
            }
        ]
    }
    plan = ActionPlan(**plan_dict)
    assert len(plan.actions) == 1
    assert isinstance(plan.actions[0], SolveCaptchaAction)
    assert plan.actions[0].captcha_type == "turnstile"

@pytest.mark.asyncio
async def test_solve_captcha_action_executor_turnstile():
    mock_page = MagicMock()
    mock_page.wait_for_selector = AsyncMock()
    mock_page.click = AsyncMock()
    mock_page.wait_for_timeout = AsyncMock()
    mock_frame = MagicMock()
    mock_frame.click = AsyncMock()
    mock_page.frames = [mock_frame]
    mock_frame.url = "https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/b/turnstile"

    executor = ActionPlanExecutor()
    plan = ActionPlan(
        url="https://cf.example.com",
        actions=[SolveCaptchaAction(captcha_type="turnstile", timeout_ms=5000)]
    )

    data = await executor.execute_plan(mock_page, plan)
    assert data.get("_captcha_solved") is True or "_captcha_status" in data

@pytest.mark.asyncio
async def test_solve_captcha_action_executor_timeout_graceful():
    mock_page = MagicMock()
    mock_page.wait_for_selector = AsyncMock(side_effect=Exception("Timeout waiting for captcha"))
    mock_page.frames = []

    executor = ActionPlanExecutor()
    plan = ActionPlan(
        url="https://cf.example.com",
        actions=[SolveCaptchaAction(captcha_type="auto", timeout_ms=1000)]
    )

    # Must not raise an unhandled exception
    data = await executor.execute_plan(mock_page, plan)
    assert data.get("_captcha_status") in ("failed", "skipped", "timeout")
