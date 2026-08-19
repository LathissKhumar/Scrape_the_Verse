from typing import Any, Optional
from app.agents.base import BaseAgent
from app.crawler.browser_executor import BrowserExecutor
from app.extraction.engine import ExtractionEngine
from app.extraction.schema import ExtractionResult, ExtractionSchema, RawPage
from app.llm.base import LLMClient
from app.models.schemas import ScrapingTask


class ExtractionAgent(BaseAgent):
    """Extraction Agent: Normalizes raw scraped content into structured records via ExtractionEngine."""

    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        engine: Optional[ExtractionEngine] = None,
        browser_executor: Optional[BrowserExecutor] = None,
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
        schema: Optional[ExtractionSchema] = None,
    ) -> ExtractionResult:
        """Extract structured records according to task schema and return ExtractionResult."""
        self.logger.info(
            f"task_id={task.task_id} Extracting structured fields ({len(task.fields)} fields) from raw content."
        )

        result: ExtractionResult = await self.engine.extract_async(
            raw_content=raw_results,
            task=task,
            schema=schema,
        )

        self.logger.info(
            f"task_id={task.task_id} Extracted {len(result.records)} record(s) using strategy '{result.strategy_used}' (fallback={result.fallback_used})."
        )
        return result
