"""Web crawler package providing production-grade, compliant browser execution and robustness."""

from leadfinder.crawler.action_executor import ActionPlanExecutor
from leadfinder.crawler.action_models import (
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
from leadfinder.crawler.block_detector import BlockDetector
from leadfinder.crawler.browser_executor import BrowserExecutor
from leadfinder.crawler.browser_manager import BrowserManager
from leadfinder.crawler.circuit_breaker import DomainCircuitBreaker
from leadfinder.crawler.config import CrawlerConfig
from leadfinder.crawler.proxy_provider import ProxyConfig, ProxyProvider
from leadfinder.crawler.rate_limiter import DomainRateLimiter
from leadfinder.crawler.result_models import BlockType, CrawlResult
from leadfinder.crawler.url_validator import SSRFSecurityError, UrlSecurityValidator

__all__ = [
    "ActionPlan",
    "ActionPlanExecutor",
    "BaseCrawlerAction",
    "BlockDetector",
    "BlockType",
    "BrowserExecutor",
    "BrowserManager",
    "ClickAction",
    "CrawlResult",
    "CrawlerAction",
    "CrawlerConfig",
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
