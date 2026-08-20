import time
from typing import Any, Optional
from uuid import uuid4

from app.brightdata.client import BrightDataClient
from app.brightdata.pipeline import BrightDataLeadPipeline
from app.config.logging import get_logger
from app.config.settings import Settings, get_settings
from app.models.schemas import ScrapingResult, ScrapingTask

logger = get_logger("BRIGHTDATA_SERVICE")


class BrightDataService:
    """High-Level Service for Bright Data Scraper Studio execution.

    Provides fast-path scraping, chained lead generation, and direct company lookups,
    completely decoupled from the local LLM multi-agent state machine.
    """

    def __init__(
        self,
        settings: Optional[Settings] = None,
        client: Optional[BrightDataClient] = None,
        pipeline: Optional[BrightDataLeadPipeline] = None,
    ):
        self._settings = settings or get_settings()
        self.client = client or BrightDataClient(settings=self._settings)
        self.pipeline = pipeline or BrightDataLeadPipeline(client=self.client, settings=self._settings)

    @property
    def is_enabled(self) -> bool:
        """Return True if Bright Data mode is active and properly configured."""
        return bool(self._settings.BRIGHTDATA and self.client.is_configured)

    async def execute_task(self, task: ScrapingTask) -> ScrapingResult:
        """Fast-path execution of a ScrapingTask using Bright Data Scraper Studio."""
        task_id = task.task_id or str(uuid4())
        start_time = time.time()
        logger.info(f"task_id={task_id} Executing fast-path Bright Data scraping for {len(task.target_urls)} URL(s)")

        if not task.target_urls:
            return ScrapingResult(
                task_id=task_id,
                status="failed",
                records=[],
                metadata={"task_id": task_id, "record_count": 0, "scraper_provider": "brightdata"},
                error="No target URLs provided in ScrapingTask.",
            )

        all_records: list[dict[str, Any]] = []
        errors: list[str] = []

        for url in task.target_urls:
            try:
                # If it's a search/discovery URL
                if "search" in url.lower() or "ss=" in url.lower() or "/impcat/" in url.lower():
                    records = await self.pipeline.run_discovery(url)
                # If it's a direct profile/company URL
                elif "profile" in url.lower() or "aboutus" in url.lower():
                    record = await self.pipeline.enrich_company(url)
                    records = [record] if record else []
                else:
                    # Default: Run Discovery Collector
                    records = await self.pipeline.run_discovery(url)

                all_records.extend(records)
            except Exception as e:
                logger.error(f"task_id={task_id} Error scraping '{url}' via Bright Data: {e}")
                errors.append(f"{url}: {str(e)}")

        elapsed_ms = round((time.time() - start_time) * 1000, 2)
        status_str = "success" if all_records else ("failed" if errors else "empty")

        logger.info(
            f"task_id={task_id} Bright Data fast-path completed in {elapsed_ms}ms | records={len(all_records)} | status={status_str}"
        )

        return ScrapingResult(
            task_id=task_id,
            status=status_str,
            records=all_records,
            metadata={
                "task_id": task_id,
                "record_count": len(all_records),
                "scraper_provider": "brightdata",
                "elapsed_ms": elapsed_ms,
                "discovery_collector_id": self.pipeline.discovery_collector_id,
                "company_collector_id": self.pipeline.company_collector_id,
            },
            error="; ".join(errors) if errors and not all_records else None,
        )

    async def generate_leads(
        self,
        query: str,
        enrich_profiles: bool = True,
        max_concurrency: int = 5,
    ) -> list[dict[str, Any]]:
        """Generate complete B2B leads by searching and enriching company profiles."""
        return await self.pipeline.generate_leads(
            query_or_url=query,
            enrich_profiles=enrich_profiles,
            max_concurrency=max_concurrency,
        )

    async def get_company_profile(self, company_url: str) -> dict[str, Any]:
        """Perform a direct lookup for a single company profile/catalog URL."""
        return await self.pipeline.enrich_company(company_url)
