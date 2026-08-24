from unittest.mock import AsyncMock, MagicMock

import pytest

from leadfinder.healing.actions.detector import ActionIssueDetector
from leadfinder.healing.actions.executor import ActionRepairExecutor
from leadfinder.healing.actions.models import ActionPlan, ActionType, PageAction
from leadfinder.healing.actions.planner import ActionRepairPlanner
from leadfinder.healing.actions.validator import ActionRepairValidator
from leadfinder.models.schemas import ScrapingTask


def test_action_issue_detector_cookie_banner():
    detector = ActionIssueDetector()
    html = """
    <html>
      <body>
        <div id="onetrust-consent-sdk">
          <button id="onetrust-accept-btn-handler">Accept All Cookies</button>
        </div>
        <div class="content"><h1>Real Products</h1></div>
      </body>
    </html>
    """
    issues = detector.detect_blocking_issues(html)
    assert len(issues) >= 1
    assert issues[0]["issue_type"] == "COOKIE_CONSENT_BANNER"
    assert issues[0]["recommended_action"] == ActionType.ACCEPT_COOKIE


def test_action_issue_detector_modal_overlay():
    detector = ActionIssueDetector()
    html = """
    <html>
      <body>
        <div class="modal-backdrop">
          <button class="dialog-close">Dismiss</button>
        </div>
      </body>
    </html>
    """
    issues = detector.detect_blocking_issues(html)
    assert any(i["issue_type"] == "BLOCKING_MODAL_OVERLAY" for i in issues)


def test_action_repair_planner_generates_plans():
    planner = ActionRepairPlanner()
    task = ScrapingTask(
        task_id="t1", objective="scrape", target_urls=["https://example.com"]
    )
    issues = [
        {
            "issue_type": "COOKIE_CONSENT_BANNER",
            "recommended_action": ActionType.ACCEPT_COOKIE,
            "target_selector": "#accept-cookies",
        },
        {
            "issue_type": "PAGINATION_LOAD_MORE_REQUIRED",
            "recommended_action": ActionType.CLICK_LOAD_MORE,
            "target_selector": ".btn-load-more",
        },
    ]
    plans = planner.plan_from_issues(issues, task)
    assert len(plans) == 2
    assert plans[0].actions[0].action_type == ActionType.CLICK
    assert plans[1].actions[1].action_type == ActionType.CLICK


@pytest.mark.asyncio
async def test_action_repair_executor_safety_and_execution():
    executor = ActionRepairExecutor()
    mock_page = MagicMock()
    mock_locator = MagicMock()
    mock_locator.scroll_into_view_if_needed = AsyncMock()
    mock_locator.click = AsyncMock()
    mock_page.locator.return_value.first = mock_locator
    mock_page.evaluate = AsyncMock()
    mock_page.content = AsyncMock(
        return_value="<html><body>Updated Content</body></html>"
    )

    plan = ActionPlan(
        description="Test Plan",
        actions=[
            PageAction(action_type=ActionType.CLICK, selector="#btn"),
            PageAction(action_type=ActionType.SCROLL, value="1000"),
            PageAction(action_type=ActionType.WAIT_MS, value="100"),
        ],
        wait_after_ms=100,
    )

    result = await executor.execute_plan(mock_page, plan)
    assert result["success"] is True
    assert len(result["actions_executed"]) == 3
    assert result["actions_executed"][0]["status"] == "success"


def test_action_repair_validator_expansion():
    validator = ActionRepairValidator()
    before_html = "<html><body><div>Small</div></body></html>"
    after_html = "<html><body><div>Small</div><div>Extra Product 1</div><div>Extra Product 2</div></body></html>"

    res = validator.evaluate_action_outcome(
        before_html=before_html,
        after_html=after_html,
        execution_result={"success": True, "actions_executed": [{"status": "success"}]},
    )
    assert res is True
