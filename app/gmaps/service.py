import time
from typing import Any, Optional
from uuid import uuid4

from app.brightdata.client import BrightDataClient
from app.config.logging import get_logger
from app.config.settings import Settings, get_settings
from app.gmaps.pipeline import GoogleMapsPipeline
from app.models.schemas import ScrapingResult, ScrapingTask

logger = get_logger("GMAPS_SERVICE")


class GoogleMapsService:
    """Standalone service for discovering and harvesting local B2B leads from Google Maps."""

    def __init__(
        self,
        settings: Optional[Settings] = None,
        client: Optional[BrightDataClient] = None,
        pipeline: Optional[GoogleMapsPipeline] = None,
    ):
        self._settings = settings or get_settings()
        self.client = client or BrightDataClient(settings=self._settings)
        self.pipeline = pipeline or GoogleMapsPipeline(client=self.client, settings=self._settings)

    @property
    def is_enabled(self) -> bool:
        return bool(self._settings.BRIGHTDATA and self.client.api_key)

    async def get_local_leads(
        self,
        query: str,
        location: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """Discover local business leads matching category and location."""
        return await self.pipeline.search_leads(query=query, location=location)

    async def execute_task(self, task: ScrapingTask) -> ScrapingResult:
        """Execute a ScrapingTask specifically targeted at Google Maps."""
        task_id = task.task_id or str(uuid4())
        start_time = time.time()
        logger.info(f"task_id={task_id} Executing Google Maps scraping task: '{task.objective}'")

        all_leads = []
        for url in task.target_urls:
            leads = await self.pipeline.search_leads(query=url)
            all_leads.extend(leads)

        elapsed_ms = round((time.time() - start_time) * 1000, 2)
        status_str = "success" if all_leads else "empty"

        return ScrapingResult(
            task_id=task_id,
            status=status_str,
            records=all_leads,
            metadata={
                "task_id": task_id,
                "record_count": len(all_leads),
                "scraper_provider": "brightdata_gmaps",
                "collector_id": self.pipeline.collector_id,
                "elapsed_ms": elapsed_ms,
            },
        )
