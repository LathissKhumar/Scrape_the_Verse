"""Data models and schemas for browser action primitives and composite action plans."""

from enum import Enum
from typing import Optional
from uuid import uuid4
from pydantic import BaseModel, Field


class ActionType(str, Enum):
    """Supported browser interaction action types for dynamic self-healing."""

    CLICK = "click"
    SCROLL = "scroll"
    SCROLL_UNTIL = "scroll_until"
    WAIT_FOR = "wait_for"
    WAIT_MS = "wait_ms"
    DISMISS_OVERLAY = "dismiss_overlay"
    ACCEPT_COOKIE = "accept_cookie"
    CLICK_LOAD_MORE = "click_load_more"
    PAGINATE_NEXT = "paginate_next"
    HOVER = "hover"


class PageAction(BaseModel):
    """Atomic page interaction instruction executed during browser action repair."""

    action_type: ActionType = Field(..., description="Action primitive category.")
    selector: Optional[str] = Field(default=None, description="Target CSS/XPath selector.")
    value: Optional[str] = Field(default=None, description="Optional payload value or scroll amount.")
    timeout_ms: int = Field(default=5000, ge=500, le=30000, description="Safe timeout for this step.")
    optional: bool = Field(default=True, description="If True, execution continues if element not found.")
    description: Optional[str] = Field(default=None, description="Human-readable rationale.")


class ActionPlan(BaseModel):
    """Composite, bounded action sequence synthesized to unblock page content or trigger dynamic hydration."""

    plan_id: str = Field(default_factory=lambda: str(uuid4()))
    actions: list[PageAction] = Field(default_factory=list, description="Ordered list of page actions (max 5).")
    description: str = Field(default="Autonomous action repair plan", description="Summary rationale.")
    wait_after_ms: int = Field(default=1000, ge=100, le=10000, description="Post-action DOM stabilization pause.")
    max_retries: int = Field(default=2, ge=1, le=3)

