import asyncio
from typing import Any, Optional
import httpx

from app.agents.base import BaseAgent
from app.brightdata.adapter import build_collector_inputs
from app.brightdata.client import BrightDataClient
from app.config.settings import get_settings
from app.crawler.browser_executor import BrowserExecutor
from app.crawler.result_models import BlockType, CrawlResult
from app.models.schemas import ScrapingTask


class ScraperAgent(BaseAgent):
    """Scraper Agent: Executes collection via Bright Data Scraper Studio or native Playwright/HTTP transport."""

    def __init__(
        self,
        brightdata_client: Optional[BrightDataClient] = None,
        browser_executor: Optional[BrowserExecutor] = None,
    ):
        super().__init__(name="SCRAPER")
        self.client = brightdata_client or BrightDataClient()
        self.browser_executor = browser_executor or BrowserExecutor()

    async def _execute_browser_scrape(self, urls: list[str]) -> list[dict[str, Any]]:
        """Execute robust parallel browser scraping using Playwright Chromium with SSRF and block detection."""
        self.logger.info(f"Executing parallel Playwright Chromium browser scrape for {len(urls)} target URL(s).")
        
        async def _crawl_single(u: str) -> dict[str, Any]:
            crawl_res: CrawlResult = await self.browser_executor.crawl(url=u)
            record: dict[str, Any] = {
                "url": crawl_res.url,
                "final_url": crawl_res.final_url,
                "html": crawl_res.html,
                "status_code": crawl_res.status_code,
                "blocked": crawl_res.blocked,
                "block_type": crawl_res.block_type.value,
                "diagnostics": crawl_res.diagnostics,
                "timing_ms": crawl_res.timing_ms,
            }
            if crawl_res.error:
                record["error"] = crawl_res.error
            if crawl_res.extracted_data:
                record["extracted_data"] = crawl_res.extracted_data
            return record

        results = await asyncio.gather(*[_crawl_single(u) for u in urls])
        return list(results)

    async def _execute_native_scrape(self, urls: list[str]) -> list[dict[str, Any]]:
        """Fallback native HTTP scraping when Bright Data API key is unconfigured."""
        return await self._execute_browser_scrape(urls)

    async def execute(self, task: ScrapingTask) -> list[dict[str, Any]]:
        """Collect raw web content for the given task target URLs."""
        if not task.target_urls:
            self.logger.error(f"task_id={task.task_id} Execution aborted: No target URLs provided.")
            raise ValueError("No target URL was supplied. URL discovery is not implemented.")

        self.logger.info(
            f"task_id={task.task_id} Received {len(task.target_urls)} target URL(s). Initiating collection."
        )

        settings = get_settings()
        provider = (task.metadata.get("scraper_provider") or settings.SCRAPER_PROVIDER or "auto").lower()

        # Check if Bright Data credentials are configured and provider is auto/brightdata
        is_configured = getattr(self.client, "is_configured", False)
        if is_configured and provider in ("auto", "brightdata"):
            inputs = build_collector_inputs(task=task)
            self.logger.info(f"task_id={task.task_id} Dispatched to Bright Data Scraper Studio (Collector: {self.client.collector_id}).")
            results = await self.client.scrape_and_collect(
                collector_id=self.client.collector_id,
                inputs=inputs,
            )
        else:
            # Native Playwright Browser execution
            results = await self._execute_browser_scrape(task.target_urls)

            # If native crawl gets blocked by anti-bot challenge and DCA is configured, fallback to DCA
            any_blocked = any(r.get("blocked", False) or r.get("status_code") in (403, 429, 503) for r in results)
            if any_blocked and is_configured:
                self.logger.warning(
                    f"task_id={task.task_id} Native browser execution encountered bot challenge/503. "
                    "Automatically escalating to Bright Data DCA cloud scraper fallback..."
                )
                inputs = build_collector_inputs(task=task)
                dca_results = await self.client.scrape_and_collect(
                    collector_id=self.client.collector_id,
                    inputs=inputs,
                )
                if dca_results:
                    results = dca_results

        self.logger.info(
            f"task_id={task.task_id} Successfully retrieved {len(results)} raw record(s)/page(s)."
        )
        return results
