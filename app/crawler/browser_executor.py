"""Browser executor coordinating URL validation, rate limiting, actions, and block detection."""

import asyncio
import logging
import time
from typing import Any, Dict, Optional
from app.crawler.action_executor import ActionPlanExecutor
from app.crawler.action_models import ActionPlan
from app.crawler.block_detector import BlockDetector
from app.crawler.browser_manager import BrowserManager
from app.crawler.circuit_breaker import DomainCircuitBreaker
from app.crawler.rate_limiter import DomainRateLimiter
from app.crawler.result_models import BlockType, CrawlResult
from app.crawler.url_validator import SSRFSecurityError, UrlSecurityValidator

logger = logging.getLogger("CRAWLER_BROWSER_EXECUTOR")


class BrowserExecutor:
    """Executes crawl requests inside an isolated Playwright context with robustness features."""

    def __init__(
        self,
        browser_manager: Optional[BrowserManager] = None,
        url_validator: Optional[UrlSecurityValidator] = None,
        rate_limiter: Optional[DomainRateLimiter] = None,
        circuit_breaker: Optional[DomainCircuitBreaker] = None,
        block_detector: Optional[BlockDetector] = None,
        action_executor: Optional[ActionPlanExecutor] = None,
    ):
        self.browser_manager = browser_manager or BrowserManager()
        self.url_validator = url_validator or UrlSecurityValidator(
            allow_private=self.browser_manager.config.allow_private_ips
        )
        self.rate_limiter = rate_limiter or DomainRateLimiter(
            requests_per_second=self.browser_manager.config.rate_limit_rps
        )
        self.circuit_breaker = circuit_breaker or DomainCircuitBreaker(
            failure_threshold=self.browser_manager.config.circuit_breaker_threshold
        )
        self.block_detector = block_detector or BlockDetector()
        self.action_executor = action_executor or ActionPlanExecutor()

    async def crawl(
        self,
        url: str,
        action_plan: Optional[ActionPlan] = None,
    ) -> CrawlResult:
        """Crawl a URL using Playwright Chromium with SSRF checks, rate limits, and block detection."""
        start_time = time.time()

        # 1. URL Security & SSRF Validation
        try:
            validated_url = self.url_validator.validate_url(url)
        except SSRFSecurityError as e:
            logger.error(f"SSRF security violation for '{url}': {e}")
            return CrawlResult(
                url=url,
                status_code=403,
                blocked=True,
                block_type=BlockType.ACCESS_DENIED,
                error=f"SSRF Security Violation: {e}",
                timing_ms=(time.time() - start_time) * 1000.0,
            )

        # 2. Circuit Breaker Check
        if not self.circuit_breaker.allow_request(validated_url):
            logger.warning(f"Domain circuit breaker is OPEN for '{validated_url}'. Crawl aborted.")
            return CrawlResult(
                url=validated_url,
                status_code=429,
                blocked=True,
                block_type=BlockType.RATE_LIMITED,
                error="Domain circuit breaker is open due to repeated consecutive blocks.",
                timing_ms=(time.time() - start_time) * 1000.0,
            )

        # 3. Domain Rate Limiting
        await self.rate_limiter.acquire(validated_url)

        # 4. Browser Context Execution
        context = await self.browser_manager.create_isolated_context()
        page = await context.new_page()

        status_code = 200
        headers_dict: Dict[str, str] = {}
        final_url = validated_url
        html_content = ""
        extracted_data: Optional[Dict[str, Any]] = None

        try:
            wait_until = action_plan.wait_until if action_plan else "domcontentloaded"
            timeout = action_plan.timeout_ms if action_plan else self.browser_manager.config.timeout_ms

            logger.info(f"Navigating to '{validated_url}' (wait_until={wait_until}, timeout={timeout}ms)...")
            response = await page.goto(validated_url, wait_until=wait_until, timeout=timeout)

            if response:
                status_code = response.status
                headers_dict = dict(response.headers)
                final_url = response.url or page.url
            else:
                final_url = page.url

            # Execute actions if plan provided
            if action_plan:
                extracted_data = await self.action_executor.execute_plan(page, action_plan)

            # Wait for lazy JS DOM rendering and client-side redirects
            try:
                await page.wait_for_load_state("domcontentloaded", timeout=5000)
            except Exception:
                pass

            # Resilient content retrieval (handles in-flight redirects gracefully)
            for attempt in range(3):
                try:
                    await page.wait_for_timeout(500)
                    html_content = await page.content()
                    final_url = page.url
                    break
                except Exception as content_err:
                    if attempt == 2:
                        raise content_err
                    await page.wait_for_timeout(1000)

        except Exception as e:
            logger.error(f"Error during browser execution for '{validated_url}': {e}")
            return CrawlResult(
                url=validated_url,
                final_url=page.url if page else validated_url,
                status_code=500,
                blocked=False,
                error=str(e),
                timing_ms=(time.time() - start_time) * 1000.0,
            )
        finally:
            await context.close()

        timing_ms = (time.time() - start_time) * 1000.0

        # 5. Block Detection
        blocked, block_type, diagnostics = self.block_detector.detect_block(
            status_code=status_code,
            headers=headers_dict,
            html=html_content,
            url=final_url,
        )

        # Record outcome in circuit breaker and rate limiter
        self.circuit_breaker.record_result(final_url, blocked=blocked, block_type=block_type)
        if block_type == BlockType.RATE_LIMITED:
            retry_after = diagnostics.get("retry_after")
            self.rate_limiter.record_429(
                final_url,
                retry_after_seconds=float(retry_after) if retry_after else None,
            )

        if blocked:
            logger.warning(f"Block detected on '{final_url}': {block_type} ({diagnostics})")

        return CrawlResult(
            url=validated_url,
            final_url=final_url,
            status_code=status_code,
            html=html_content,
            blocked=blocked,
            block_type=block_type,
            diagnostics=diagnostics,
            timing_ms=timing_ms,
            extracted_data=extracted_data,
        )
