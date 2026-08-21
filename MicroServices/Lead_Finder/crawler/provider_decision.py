"""Intelligent anti-bot and provider recovery decision engine."""

from enum import Enum
from typing import Any, Optional
from leadfinder.config.logging import get_logger
from leadfinder.crawler.result_models import BlockType, CrawlResult

logger = get_logger("PROVIDER_DECISION_ENGINE")


class FailureNature(str, Enum):
    """Categorized nature of a crawl failure."""

    TRANSIENT_NETWORK = "transient_network"
    TIMEOUT = "timeout"
    JS_RENDERING = "js_rendering"
    BOT_BLOCKED = "bot_blocked"
    RATE_LIMITED = "rate_limited"
    AUTH_REQUIRED = "auth_required"
    INVALID_PAGE = "invalid_page"
    UNKNOWN = "unknown"


class ProviderRecommendation(str, Enum):
    """Action recommendation for resolving a crawl failure."""

    LOCAL_RETRY_BACKOFF = "local_retry_backoff"
    INCREASE_TIMEOUT = "increase_timeout"
    BRIGHTDATA_FALLBACK = "brightdata_fallback"
    ABORT = "abort"
    NORMAL_HEALING = "normal_healing"


class ProviderDecisionEngine:
    """Classifies crawl failures to intelligently balance local retries against cloud scraper proxies."""

    def __init__(self):
        self._domain_stats: dict[str, dict[str, Any]] = {}

    def classify_failure(self, crawl_result: CrawlResult) -> FailureNature:
        """Categorize the exact nature of the failure from status code, headers, and DOM."""
        if crawl_result.blocked:
            if crawl_result.block_type == BlockType.RATE_LIMITED:
                return FailureNature.RATE_LIMITED
            if crawl_result.block_type in (BlockType.CAPTCHA, BlockType.SECURITY_CHALLENGE, BlockType.ACCESS_DENIED):
                return FailureNature.BOT_BLOCKED
            if crawl_result.block_type == BlockType.AUTH_REQUIRED:
                return FailureNature.AUTH_REQUIRED

        status = crawl_result.status_code
        err = (crawl_result.error or "").lower()

        if "timeout" in err or status in (408, 504):
            return FailureNature.TIMEOUT
        if "network" in err or "econnreset" in err or "enotfound" in err or status in (502,):
            return FailureNature.TRANSIENT_NETWORK
        if status in (404, 410):
            return FailureNature.INVALID_PAGE
        if not crawl_result.html or len(crawl_result.html) < 200:
            return FailureNature.JS_RENDERING

        return FailureNature.UNKNOWN

    def decide_action(
        self,
        crawl_result: CrawlResult,
        attempt: int = 1,
        brightdata_configured: bool = False,
    ) -> tuple[ProviderRecommendation, str]:
        """Determine next recovery action based on failure nature and attempt budget."""
        nature = self.classify_failure(crawl_result)
        logger.info(f"Crawl failure classified as '{nature.value}' on attempt {attempt}")

        # 1. Bot block or Rate limit -> fallback to Bright Data if available
        if nature in (FailureNature.BOT_BLOCKED, FailureNature.RATE_LIMITED):
            if brightdata_configured:
                return ProviderRecommendation.BRIGHTDATA_FALLBACK, "WAF/CAPTCHA challenge detected; escalating to Bright Data DCA cloud scraper."
            return ProviderRecommendation.ABORT, "Bot blocked and cloud proxy unconfigured."

        # 2. Transient network failure -> local retry with backoff
        if nature == FailureNature.TRANSIENT_NETWORK and attempt <= 2:
            return ProviderRecommendation.LOCAL_RETRY_BACKOFF, f"Transient network issue; retrying locally with backoff (attempt {attempt})."

        # 3. Timeout -> increase timeout locally
        if nature == FailureNature.TIMEOUT and attempt <= 2:
            return ProviderRecommendation.INCREASE_TIMEOUT, f"Page load timeout; retrying with extended timeout (attempt {attempt})."

        # 4. Incomplete JS rendering -> normal healing with action/crawler adaptation
        if nature == FailureNature.JS_RENDERING:
            return ProviderRecommendation.NORMAL_HEALING, "Empty or partial DOM; proceeding to crawler/action healing."

        return ProviderRecommendation.NORMAL_HEALING, "Proceeding to standard diagnosis and extraction healing."
