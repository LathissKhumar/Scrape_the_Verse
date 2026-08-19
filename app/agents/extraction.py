from typing import Any, Optional
from app.agents.base import BaseAgent
from app.llm.base import LLMClient
from app.models.schemas import ScrapingTask


class ExtractionAgent(BaseAgent):
    """Extraction Agent: Extracts and normalizes structured records from raw scrape data (Phase 3)."""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        super().__init__(name="EXTRACTION")
        self.llm_client = llm_client

    async def extract(
        self,
        raw_results: list[dict[str, Any]],
        task: ScrapingTask,
    ) -> list[dict[str, Any]]:
        """Normalize raw scraped payloads into structured records matching task.fields/output_schema.

        TODO (Phase 3):
        1. Inspect raw scraped payloads (HTML/JSON/text).
        2. Apply heuristic parsers or LLM extraction according to task.output_schema.
        3. Clean and normalize data types (strings, numbers, URLs).
        4. Return canonical list of records.
        """
        raise NotImplementedError("ExtractionAgent execution will be implemented in Phase 3.")
