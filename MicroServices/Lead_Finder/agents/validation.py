from typing import Any, Optional

from leadfinder.agents.base import BaseAgent
from leadfinder.models.schemas import ScrapingTask
from leadfinder.validation.baseline import HistoricalBaseline
from leadfinder.validation.engine import ValidationEngine
from leadfinder.validation.schemas import ValidationResult


class ValidationAgent(BaseAgent):
    """Validation Agent: Evaluates extracted records, computes health scores, and records failure diagnostics."""

    def __init__(self, engine: Optional[ValidationEngine] = None):
        super().__init__(name="VALIDATION")
        self.engine = engine or ValidationEngine()

    async def validate(
        self,
        extracted_results: list[dict[str, Any]],
        task: ScrapingTask,
        raw_results: Optional[Any] = None,
        historical_baseline: Optional[HistoricalBaseline] = None,
    ) -> ValidationResult:
        """Execute deterministic data validation and return complete ValidationResult."""
        self.logger.debug(
            f"task_id={task.task_id} Evaluating quality and health for {len(extracted_results)} extracted record(s)."
        )

        result: ValidationResult = self.engine.validate(
            records=extracted_results,
            task=task,
            raw_results=raw_results,
            historical_baseline=historical_baseline,
        )

        self.logger.info(
            f"Quality audit completed | status={result.status} | health_score={result.health_score:.2f} | quality_score={result.quality_score:.2f} | anomalies={len(result.anomalies)}"
        )
        return result

