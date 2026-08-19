from typing import Any, Optional
from app.agents.base import BaseAgent
from app.brightdata.client import BrightDataClient
from app.models.schemas import ScrapingTask


class ScraperAgent(BaseAgent):
    """Scraper Agent: Dispatches scraping tasks to Bright Data Scraper Studio (Phase 2)."""

    def __init__(self, brightdata_client: Optional[BrightDataClient] = None):
        super().__init__(name="SCRAPER")
        self.brightdata_client = brightdata_client or BrightDataClient()

    async def execute(self, task: ScrapingTask) -> list[dict[str, Any]]:
        """Dispatch task to Bright Data client and collect raw results.

        TODO (Phase 2):
        1. Format target URLs and parameters into Bright Data payload.
        2. Trigger collector run via self.brightdata_client.trigger_scraper.
        3. Poll job status until completion via self.brightdata_client.get_job_status.
        4. Fetch and return raw results via self.brightdata_client.fetch_results.
        """
        raise NotImplementedError("ScraperAgent execution will be implemented in Phase 2.")
