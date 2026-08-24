import pytest
from pydantic import ValidationError

from leadfinder.crawler.action_models import (
    ActionPlan,
    ClickAction,
    ExtractAction,
    FillAction,
    NavigateAction,
    ScrollAction,
    SelectAction,
    WaitForAction,
)
from leadfinder.crawler.result_models import BlockType, CrawlResult


def test_action_plan_validation():
    plan = ActionPlan(
        url="https://example.com",
        actions=[
            NavigateAction(url="https://example.com"),
            WaitForAction(selector=".product-item", timeout_ms=5000),
            ScrollAction(max_iterations=3, delay_ms=500),
            ClickAction(selector="button.load-more"),
            FillAction(selector="input.search", text="test query"),
            SelectAction(selector="select.currency", value="USD"),
            ExtractAction(fields={"title": "h1", "price": ".price"}),
        ],
    )
    assert len(plan.actions) == 7
    assert plan.actions[0].action_type == "navigate"
    assert plan.actions[1].action_type == "wait_for"
    assert plan.actions[2].action_type == "scroll"


def test_disallow_arbitrary_code_injection():
    with pytest.raises(ValidationError):
        ActionPlan.model_validate(
            {
                "url": "https://example.com",
                "actions": [{"action_type": "eval_arbitrary_code", "code": "alert(1)"}],
            }
        )


def test_crawl_result_model():
    res = CrawlResult(
        url="https://example.com",
        final_url="https://example.com/home",
        status_code=200,
        html="<html><body><h1>Title</h1></body></html>",
        markdown="# Title",
        blocked=False,
        block_type=BlockType.NONE,
        timing_ms=120.5,
    )
    assert res.success is True
    assert res.blocked is False
    assert res.block_type == BlockType.NONE
    assert res.timing_ms == 120.5
