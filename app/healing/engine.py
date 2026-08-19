from typing import Any, Optional
from urllib.parse import urlparse
from app.config.logging import get_logger
from app.diagnosis.schemas import DiagnosisResult
from app.extraction.engine import ExtractionEngine
from app.extraction.schema import ExtractionSchema, RawPage
from app.healing.evaluator import RepairEvaluator
from app.healing.evidence_collector import RepairEvidenceCollector
from app.healing.executor import RepairExecutor
from app.healing.memory import RepairMemory
from app.healing.patcher import RepairPatcher
from app.healing.planner import HealingPlanner
from app.healing.schemas import (
    PerformanceSnapshot,
    RepairEvaluation,
    RepairMemoryRecord,
    RepairPlan,
    RepairType,
)
from app.models.schemas import ScrapingTask
from app.validation.engine import ValidationEngine
from app.validation.schemas import ValidationResult

logger = get_logger("HEALING_ENGINE")


class HealingEngine:
    """Autonomous Self-Healing Engine coordinating evidence collection, candidate ranking, canary execution, deterministic evaluation, and repair memory."""

    def __init__(
        self,
        evidence_collector: Optional[RepairEvidenceCollector] = None,
        planner: Optional[HealingPlanner] = None,
        executor: Optional[RepairExecutor] = None,
        evaluator: Optional[RepairEvaluator] = None,
        memory: Optional[RepairMemory] = None,
        extraction_engine: Optional[ExtractionEngine] = None,
        validation_engine: Optional[ValidationEngine] = None,
        max_repair_attempts: int = 3,
    ):
        self.evidence_collector = evidence_collector or RepairEvidenceCollector()
        self.planner = planner or HealingPlanner()
        self.executor = executor or RepairExecutor()
        self.evaluator = evaluator or RepairEvaluator()
        self.memory = memory or RepairMemory()
        self.extraction_engine = extraction_engine or ExtractionEngine()
        self.validation_engine = validation_engine or ValidationEngine()
        self.max_repair_attempts = max_repair_attempts

    async def heal(
        self,
        task: ScrapingTask,
        diagnosis: DiagnosisResult,
        validation: ValidationResult,
        current_schema: ExtractionSchema,
        scraper_config: Optional[dict[str, Any]] = None,
        raw_results: Optional[list[dict[str, Any]]] = None,
    ) -> tuple[bool, Optional[ExtractionSchema], RepairEvaluation, list[dict[str, Any]], list[dict[str, Any]]]:
        """Execute autonomous self-healing loop:

        Returns:
            (success, healed_schema, final_evaluation, extracted_records, repair_history)
        """
        task_id = task.task_id
        logger.info(f"Starting self-healing loop for task_id={task_id} (root_cause={diagnosis.root_cause.value})")

        repair_history: list[dict[str, Any]] = []

        # Step 1: Collect fresh live page evidence & check for transient recovery
        raw_pages, is_recovered, recovery_val = await self.evidence_collector.check_transient_recovery(
            task=task,
            schema=current_schema,
        )

        if not raw_pages and raw_results:
            raw_pages = [RawPage(**r) for r in raw_results]

        if is_recovered and recovery_val:
            logger.info(f"Task {task_id} recovered transiently without repair needed.")
            no_rep_plan = RepairPlan(
                repair_type=RepairType.NO_REPAIR_REQUIRED,
                reason="Fresh scrape recovered healthy performance without configuration modification",
                confidence=1.0,
            )
            eval_res = self.evaluator.evaluate(
                before=validation,
                after=recovery_val,
                diagnosis=diagnosis,
                plan=no_rep_plan,
            )
            eval_res.accepted = True

            # Extract records for returned output
            ext_res = await self.extraction_engine.extract(
                raw_results=[p.model_dump() for p in raw_pages],
                task=task,
                schema=current_schema,
            )

            repair_history.append({
                "attempt": 1,
                "repair_type": RepairType.NO_REPAIR_REQUIRED.value,
                "confidence": 1.0,
                "health_before": validation.health_score,
                "health_after": recovery_val.health_score,
                "accepted": True,
            })
            return True, current_schema, eval_res, ext_res.records, repair_history

        # Step 2: Generate candidate repair plans
        candidates = await self.planner.generate_candidates(
            task=task,
            diagnosis=diagnosis,
            validation=validation,
            raw_pages=raw_pages,
            current_schema=current_schema,
            failed_attempts=repair_history,
        )

        if not candidates:
            logger.warning(f"No repair candidates could be generated for task {task_id}.")
            fallback_eval = RepairEvaluation(
                repair_id="none",
                before=self.evaluator.snapshot(validation),
                after=self.evaluator.snapshot(validation),
                improvement=0.0,
                critical_failure_resolved=False,
                regression_detected=False,
                accepted=False,
                rejection_reason="No viable repair candidates generated",
            )
            return False, None, fallback_eval, [], repair_history

        # Step 3: Bounded repair candidate execution and canary validation
        attempts_budget = min(len(candidates), self.max_repair_attempts)
        last_eval: Optional[RepairEvaluation] = None

        for attempt_idx in range(attempts_budget):
            candidate = candidates[attempt_idx]
            plan = candidate.plan
            attempt_num = attempt_idx + 1

            logger.info(
                f"[Attempt {attempt_num}/{attempts_budget}] Testing candidate repair: "
                f"{plan.repair_type.value} (score={candidate.score:.2f}, source={candidate.source})"
            )

            # Apply candidate configuration
            candidate_schema, updated_scraper_config = self.executor.apply_candidate(
                plan=plan,
                schema=current_schema,
                scraper_config=scraper_config,
            )

            # Canary execution: extract with candidate schema
            raw_dicts = [p.model_dump() for p in raw_pages]
            canary_extraction = await self.extraction_engine.extract(
                raw_results=raw_dicts,
                task=task,
                schema=candidate_schema,
            )

            # Canary validation: validate extracted records
            canary_validation = await self.validation_engine.validate(
                extracted_results=canary_extraction.records,
                task=task,
                raw_results=raw_dicts,
            )

            # Deterministic repair evaluation
            evaluation = self.evaluator.evaluate(
                before=validation,
                after=canary_validation,
                diagnosis=diagnosis,
                plan=plan,
                strategy_used=canary_extraction.strategy_used,
            )
            last_eval = evaluation

            attempt_record = {
                "attempt": attempt_num,
                "repair_type": plan.repair_type.value,
                "confidence": plan.confidence,
                "health_before": validation.health_score,
                "health_after": canary_validation.health_score,
                "accepted": evaluation.accepted,
                "rejection_reason": evaluation.rejection_reason,
            }
            repair_history.append(attempt_record)

            if evaluation.accepted:
                logger.info(
                    f"Candidate repair accepted for task_id={task_id} on attempt {attempt_num}! "
                    f"health: {validation.health_score:.2f} -> {canary_validation.health_score:.2f}"
                )
                # Persist to memory for future site visits
                target_url = task.target_urls[0] if task.target_urls else "https://example.com"
                domain = urlparse(target_url).netloc.lower()
                sample_html = raw_pages[0].get_primary_content() if raw_pages else ""
                sig = self.memory.generate_signature(
                    url=target_url,
                    html=sample_html,
                    fields=[f.name for f in candidate_schema.fields],
                )
                self.memory.record_success(
                    RepairMemoryRecord(
                        domain=domain,
                        signature=sig,
                        root_cause=diagnosis.root_cause.value,
                        repair_type=plan.repair_type,
                        successful_patch=plan.proposed_configuration,
                        health_before=validation.health_score,
                        health_after=canary_validation.health_score,
                        strategy=canary_extraction.strategy_used,
                    )
                )
                return True, candidate_schema, evaluation, canary_extraction.records, repair_history

            logger.warning(
                f"Candidate repair rejected on attempt {attempt_num}: {evaluation.rejection_reason}"
            )

        # All attempts exhausted
        logger.error(f"Self-healing exhausted {attempts_budget} attempt(s) for task_id={task_id}. Escalating.")
        if not last_eval:
            last_eval = RepairEvaluation(
                repair_id="exhausted",
                before=self.evaluator.snapshot(validation),
                after=self.evaluator.snapshot(validation),
                improvement=0.0,
                critical_failure_resolved=False,
                regression_detected=False,
                accepted=False,
                rejection_reason="Max repair attempts exhausted without acceptable improvement",
            )

        return False, None, last_eval, [], repair_history
