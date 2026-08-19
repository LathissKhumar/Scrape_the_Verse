from typing import Any, Optional
import httpx

from app.agents.base import BaseAgent
from app.brightdata.adapter import build_collector_inputs
from app.brightdata.client import BrightDataClient
from app.config.settings import get_settings
from app.models.schemas import ScrapingTask


class ScraperAgent(BaseAgent):
    """Scraper Agent: Executes collection via Bright Data Scraper Studio or native HTTP transport fallback."""

    def __init__(self, brightdata_client: Optional[BrightDataClient] = None):
        super().__init__(name="SCRAPER")
        self.client = brightdata_client or BrightDataClient()

    async def _execute_native_scrape(self, urls: list[str]) -> list[dict[str, Any]]:
        """Fallback native HTTP scraping when Bright Data API key is unconfigured."""
        self.logger.info(f"Bright Data unconfigured. Executing native HTTP scrape for {len(urls)} target URL(s).")
        results: list[dict[str, Any]] = []

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
        }

        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True, headers=headers) as client:
            for u in urls:
                try:
                    resp = await client.get(u)
                    results.append({
                        "url": u,
                        "html": resp.text,
                        "status_code": resp.status_code,
                        "headers": dict(resp.headers),
                    })
                except Exception as e:
                    self.logger.warning(f"Native fetch failed for {u}: {e}")
                    results.append({
                        "url": u,
                        "html": "",
                        "error": str(e),
                    })

        return results

    async def execute(self, task: ScrapingTask) -> list[dict[str, Any]]:
        """Collect raw web content for the given task target URLs."""
        if not task.target_urls:
            self.logger.error(f"task_id={task.task_id} Execution aborted: No target URLs provided.")
            raise ValueError("No target URL was supplied. URL discovery is not implemented.")

        self.logger.info(
            f"task_id={task.task_id} Received {len(task.target_urls)} target URL(s). Initiating collection."
        )

        # Check if Bright Data credentials are configured
        is_configured = getattr(self.client, "is_configured", False)
        if is_configured:
            inputs = build_collector_inputs(task=task)
            self.logger.info(f"task_id={task.task_id} Dispatched to Bright Data Scraper Studio.")
            collector_id = "c_default"
            if hasattr(self.client, "settings") and hasattr(self.client.settings, "brightdata_collector_id"):
                collector_id = self.client.settings.brightdata_collector_id
            results = await self.client.scrape_and_collect(
                collector_id=collector_id,
                inputs=inputs,
            )
        else:
            # Native fallback
            results = await self._execute_native_scrape(task.target_urls)

        self.logger.info(
            f"task_id={task.task_id} Successfully retrieved {len(results)} raw record(s)/page(s)."
        )
        return results
