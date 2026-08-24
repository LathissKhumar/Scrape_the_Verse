"""Declarative, allowlisted action models for browser automation without arbitrary code execution."""

from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field


class BaseCrawlerAction(BaseModel):
    """Base class for all strictly allowlisted browser actions."""


class NavigateAction(BaseCrawlerAction):
    action_type: Literal["navigate"] = "navigate"
    url: str
    timeout_ms: int = Field(default=30000, ge=100, le=120000)


class WaitForAction(BaseCrawlerAction):
    action_type: Literal["wait_for"] = "wait_for"
    selector: str | None = None
    state: Literal["attached", "detached", "visible", "hidden"] = "visible"
    timeout_ms: int = Field(default=10000, ge=100, le=60000)


class ClickAction(BaseCrawlerAction):
    action_type: Literal["click"] = "click"
    selector: str
    timeout_ms: int = Field(default=5000, ge=100, le=30000)


class FillAction(BaseCrawlerAction):
    action_type: Literal["fill"] = "fill"
    selector: str
    text: str
    timeout_ms: int = Field(default=5000, ge=100, le=30000)


class SelectAction(BaseCrawlerAction):
    action_type: Literal["select"] = "select"
    selector: str
    value: str
    timeout_ms: int = Field(default=5000, ge=100, le=30000)


class ScrollAction(BaseCrawlerAction):
    action_type: Literal["scroll"] = "scroll"
    max_iterations: int = Field(default=5, ge=1, le=20)
    delay_ms: int = Field(default=500, ge=50, le=5000)
    distance_px: int = Field(default=800, ge=100, le=5000)


class ExtractAction(BaseCrawlerAction):
    action_type: Literal["extract"] = "extract"
    fields: dict[str, str] = Field(description="Map of field name to CSS selector")


class SolveCaptchaAction(BaseCrawlerAction):
    action_type: Literal["solve_captcha"] = "solve_captcha"
    captcha_type: Literal["turnstile", "recaptcha", "hcaptcha", "image", "auto"] = (
        "auto"
    )
    selector: str | None = None
    timeout_ms: int = Field(default=15000, ge=1000, le=60000)
    solver_config: dict[str, Any] = Field(default_factory=dict)


CrawlerAction = Annotated[
    NavigateAction
    | WaitForAction
    | ClickAction
    | FillAction
    | SelectAction
    | ScrollAction
    | ExtractAction
    | SolveCaptchaAction,
    Field(discriminator="action_type"),
]


class ActionPlan(BaseModel):
    """Declarative action sequence for a web crawl."""

    url: str
    actions: list[CrawlerAction] = Field(default_factory=list)
    wait_until: Literal["load", "domcontentloaded", "networkidle", "commit"] = (
        "domcontentloaded"
    )
    timeout_ms: int = Field(default=30000, ge=1000, le=120000)
