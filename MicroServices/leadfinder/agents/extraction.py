from typing import Any

from leadfinder.agents.base import BaseAgent
from leadfinder.crawler.browser_executor import BrowserExecutor
from leadfinder.extraction.engine import ExtractionEngine
from leadfinder.extraction.schema import ExtractionResult, ExtractionSchema
from leadfinder.llm.base import LLMClient
from leadfinder.models.schemas import ScrapingTask


class ExtractionAgent(BaseAgent):
    """Extraction Agent: Normalizes raw scraped content into structured records via ExtractionEngine."""

    def __init__(
        self,
        llm_client: LLMClient | None = None,
        engine: ExtractionEngine | None = None,
        browser_executor: BrowserExecutor | None = None,
    ):
        super().__init__(name="EXTRACTION")
        self.engine = engine or ExtractionEngine(
            llm_client=llm_client,
            browser_executor=browser_executor or BrowserExecutor(),
        )

    async def extract(
        self,
        raw_results: Any,
        task: ScrapingTask,
        schema: ExtractionSchema | None = None,
    ) -> ExtractionResult:
        """Extract structured records according to task schema and return ExtractionResult."""
        self.logger.debug(
            f"task_id={task.task_id} Extracting structured fields ({len(task.fields)} fields) from raw content."
        )

        result: ExtractionResult = await self.engine.extract_async(
            raw_content=raw_results,
            task=task,
            schema=schema,
        )

        self.logger.info(
            f"Data extracted | strategy={result.strategy_used} | fields={len(task.fields)} | records={len(result.records)}"
        )
        return result
