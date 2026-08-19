"""Web crawler package providing production-grade, compliant browser execution and robustness."""

from app.crawler.action_executor import ActionPlanExecutor
from app.crawler.action_models import (
    ActionPlan,
    ClickAction,
    CrawlerAction,
    ExtractAction,
    FillAction,
    NavigateAction,
    ScrollAction,
    SelectAction,
    WaitForAction,
)
from app.crawler.block_detector import BlockDetector
from app.crawler.browser_executor import BrowserExecutor
from app.crawler.browser_manager import BrowserManager
from app.crawler.circuit_breaker import DomainCircuitBreaker
from app.crawler.config import CrawlerConfig
from app.crawler.proxy_provider import ProxyConfig, ProxyProvider
from app.crawler.rate_limiter import DomainRateLimiter
from app.crawler.result_models import BlockType, CrawlResult
from app.crawler.url_validator import SSRFSecurityError, UrlSecurityValidator

__all__ = [
    "ActionPlan",
    "ActionPlanExecutor",
    "BaseCrawlerAction",
    "BlockDetector",
    "BlockType",
    "BrowserExecutor",
    "BrowserManager",
    "ClickAction",
    "CrawlerAction",
    "CrawlerConfig",
    "CrawlResult",
    "DomainCircuitBreaker",
    "DomainRateLimiter",
    "ExtractAction",
    "FillAction",
    "NavigateAction",
    "ProxyConfig",
    "ProxyProvider",
    "SSRFSecurityError",
    "ScrollAction",
    "SelectAction",
    "UrlSecurityValidator",
    "WaitForAction",
]
