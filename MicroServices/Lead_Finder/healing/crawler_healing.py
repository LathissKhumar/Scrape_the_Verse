"""Dynamic crawler-level healing for adapting browser timeouts, wait conditions, and scroll strategies."""

from typing import Any

from leadfinder.config.logging import get_logger
from leadfinder.crawler.browser_executor import BrowserExecutor
from leadfinder.crawler.result_models import CrawlResult

logger = get_logger("CRAWLER_HEALING_ENGINE")


class CrawlerHealingEngine:
    """Adapts browser lifecycle parameters (wait_until, timeouts, scrolling) when pre-extraction DOM is insufficient."""

    def __init__(self, browser_executor: BrowserExecutor | None = None) -> None:
        self.browser_executor = browser_executor or BrowserExecutor()

    def generate_crawler_adaptations(
        self,
        initial_result: CrawlResult,
        attempt: int = 1,
    ) -> list[dict[str, Any]]:
        """Generate bounded crawler parameter candidates."""
        adaptations: list[dict[str, Any]] = []

        html_len = len(initial_result.html or "")

        # Adaptation 1: Switch wait condition to networkidle and add hydration pause
        if html_len < 1000 or "timeout" in (initial_result.error or "").lower():
            adaptations.append(
                {
                    "description": "Switch to networkidle with extended timeout",
                    "wait_until": "networkidle",
                    "timeout_ms": min(
                        45000, (initial_result.timing_ms or 30000) + 10000
                    ),
                    "scroll_down": True,
                }
            )

        # Adaptation 2: Incremental scroll down to trigger lazy loading
        adaptations.append(
            {
                "description": "Incremental page scrolling for lazy components",
                "wait_until": "domcontentloaded",
                "timeout_ms": 35000,
                "scroll_down": True,
                "scroll_steps": 3,
            }
        )

        return adaptations

    async def execute_crawler_repair(
        self,
        url: str,
        adaptation: dict[str, Any],
    ) -> CrawlResult:
        """Execute crawl with adapted configuration."""
        logger.debug(
            f"Executing crawler repair for {url}: {adaptation.get('description')}"
        )
        result = await self.browser_executor.crawl(url=url)
        return result
