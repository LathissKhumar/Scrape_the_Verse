from typing import Any, Optional
from app.agents.base import BaseAgent
from app.brightdata.adapter import build_collector_inputs
from app.brightdata.client import BrightDataClient
from app.models.schemas import ScrapingTask


class ScraperAgent(BaseAgent):
    """Scraper Agent: Dispatches validated scraping tasks to Bright Data Scraper Studio."""

    def __init__(self, brightdata_client: Optional[BrightDataClient] = None):
        super().__init__(name="SCRAPER")
        self.brightdata_client = brightdata_client or BrightDataClient()

    async def execute(
        self,
        task: ScrapingTask,
        collector_id: Optional[str] = None,
        poll_interval: float = 2.0,
        max_poll_seconds: float = 120.0,
    ) -> list[dict[str, Any]]:
        """Dispatch task to Bright Data client and collect raw structured records.

        Steps:
        1. Validate target URLs exist in task.
        2. Convert task to collector inputs using Bright Data adapter.
        3. Trigger and poll collection until completion.
        4. Normalize and return records.
        """
        if not task.target_urls:
            self.logger.error(f"Task {task.task_id} contains no target URLs.")
            raise ValueError(f"Task {task.task_id} contains no target URLs.")

        self.logger.info(
            f"task_id={task.task_id} Received {len(task.target_urls)} target URL(s). Preparing collector inputs."
        )
        collector_inputs = build_collector_inputs(task)

        self.logger.info(
            f"task_id={task.task_id} Executing Bright Data scrape job for {len(collector_inputs)} input(s)..."
        )
        raw_records = await self.brightdata_client.scrape_and_collect(
            collector_id=collector_id,
            inputs=collector_inputs,
            poll_interval=poll_interval,
            max_poll_seconds=max_poll_seconds,
        )

        normalized_records: list[dict[str, Any]] = []
        if isinstance(raw_records, list):
            for item in raw_records:
                if isinstance(item, dict):
                    normalized_records.append(item)
                else:
                    normalized_records.append({"raw_value": item})
        elif isinstance(raw_records, dict):
            normalized_records.append(raw_records)

        self.logger.info(
            f"task_id={task.task_id} Retrieved {len(normalized_records)} record(s) from Bright Data."
        )
        return normalized_records
