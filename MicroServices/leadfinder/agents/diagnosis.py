from typing import Any, Optional

from app.agents.base import BaseAgent
from app.diagnosis.engine import DiagnosisEngine
from app.diagnosis.schemas import DiagnosisResult
from app.llm.base import LLMClient
from app.models.schemas import ScrapingTask
from app.validation.schemas import ValidationResult


class DiagnosisAgent(BaseAgent):
    """Diagnosis Agent: Analyzes failures, identifies root causes, and recommends adaptive repair plans."""

    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        engine: Optional[DiagnosisEngine] = None,
    ):
        super().__init__(name="DIAGNOSIS")
        self.engine = engine or DiagnosisEngine(llm_client=llm_client)

    async def diagnose(
        self,
        task: ScrapingTask,
        validation_result: ValidationResult,
        raw_results: Optional[Any] = None,
        extracted_results: Optional[list[dict[str, Any]]] = None,
        scraper_metadata: Optional[dict[str, Any]] = None,
    ) -> DiagnosisResult:
        """Analyze validation results and evidence to produce structured DiagnosisResult."""
        self.logger.debug(
            f"task_id={task.task_id} Diagnosing failure for status='{validation_result.status}', health_score={validation_result.health_score}."
        )

        result: DiagnosisResult = await self.engine.diagnose_async(
            task=task,
            validation_result=validation_result,
            raw_results=raw_results,
            extracted_results=extracted_results,
            scraper_metadata=scraper_metadata,
        )

        self.logger.info(
            f"Degradation diagnosed | root_cause={result.root_cause.value} | confidence={result.confidence:.2f} | repair_strategy={result.repair_strategy.value}"
        )
        return result

