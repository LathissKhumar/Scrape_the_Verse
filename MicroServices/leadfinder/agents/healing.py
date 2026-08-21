from typing import Any, Optional
from leadfinder.agents.base import BaseAgent
from leadfinder.config.logging import get_logger
from leadfinder.diagnosis.schemas import DiagnosisResult
from leadfinder.extraction.engine import ExtractionEngine
from leadfinder.extraction.schema import ExtractionSchema, RawPage
from leadfinder.healing.engine import HealingEngine
from leadfinder.healing.evaluator import RepairEvaluator
from leadfinder.healing.evidence_collector import RepairEvidenceCollector
from leadfinder.healing.executor import RepairExecutor
from leadfinder.healing.memory import RepairMemory
from leadfinder.healing.patcher import RepairPatcher
from leadfinder.healing.planner import HealingPlanner
from leadfinder.healing.schemas import RepairEvaluation
from leadfinder.llm.base import LLMClient
from leadfinder.models.schemas import ScrapingTask
from leadfinder.validation.engine import ValidationEngine
from leadfinder.validation.schemas import ValidationResult

logger = get_logger("HEALING_AGENT")


class HealingAgent(BaseAgent):
    """Healing Agent: Orchestrates autonomous self-healing of scraping and extraction failures."""

    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        scraper_agent: Optional[Any] = None,
        extraction_engine: Optional[ExtractionEngine] = None,
        validation_engine: Optional[ValidationEngine] = None,
        memory: Optional[RepairMemory] = None,
        max_repair_attempts: int = 3,
    ):
        super().__init__(name="HEALING")
        self.llm_client = llm_client
        self.memory = memory or RepairMemory()
        self.evidence_collector = RepairEvidenceCollector(
            scraper_agent=scraper_agent,
            extraction_engine=extraction_engine,
            validation_engine=validation_engine,
        )
        self.planner = HealingPlanner(
            llm_client=llm_client,
            memory=self.memory,
        )
        self.executor = RepairExecutor()
        self.evaluator = RepairEvaluator()
        self.engine = HealingEngine(
            evidence_collector=self.evidence_collector,
            planner=self.planner,
            executor=self.executor,
            evaluator=self.evaluator,
            memory=self.memory,
            extraction_engine=extraction_engine or ExtractionEngine(),
            validation_engine=validation_engine or ValidationEngine(),
            max_repair_attempts=max_repair_attempts,
        )

    async def heal(
        self,
        task: ScrapingTask,
        diagnosis: DiagnosisResult,
        validation: ValidationResult,
        current_schema: Optional[ExtractionSchema] = None,
        raw_results: Optional[list[dict[str, Any]]] = None,
        scraper_config: Optional[dict[str, Any]] = None,
    ) -> tuple[bool, Optional[ExtractionSchema], RepairEvaluation, list[dict[str, Any]], list[dict[str, Any]]]:
        """Execute self-healing loop for the given task and diagnostic failure report."""
        schema = current_schema or ExtractionSchema()
        success, healed_schema, evaluation, healed_records, history = await self.engine.heal(
            task=task,
            diagnosis=diagnosis,
            validation=validation,
            current_schema=schema,
            scraper_config=scraper_config,
            raw_results=raw_results,
        )
        if success:
            repair_type_name = history[-1]["repair_type"] if history else "UNKNOWN"
            self.logger.info(
                f"Self-healing succeeded | repair_type={repair_type_name} | health={evaluation.before.health:.2f} -> {evaluation.after.health:.2f} | accepted=True"
            )
        else:
            self.logger.warning(
                f"Self-healing exhausted | attempts={len(history)} | initial_health={validation.health_score:.2f} | reason={evaluation.rejection_reason or 'exhausted'}"
            )
        return success, healed_schema, evaluation, healed_records, history

