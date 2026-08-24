"""Autonomous Self-Healing Engine coordinating evidence collection, candidate ranking, canary execution, deterministic evaluation, multi-page validation, and repair memory."""

import json
import time
from typing import Any
from urllib.parse import urlparse

from leadfinder.config.logging import get_logger
from leadfinder.diagnosis.schemas import DiagnosisResult
from leadfinder.extraction.engine import ExtractionEngine
from leadfinder.extraction.schema import ExtractionSchema, RawPage
from leadfinder.healing.actions.executor import ActionRepairExecutor
from leadfinder.healing.evaluator import RepairEvaluator
from leadfinder.healing.evidence_collector import RepairEvidenceCollector
from leadfinder.healing.executor import RepairExecutor
from leadfinder.healing.failed_memory import FailedRepairMemory
from leadfinder.healing.fingerprint import DOMFingerprinter
from leadfinder.healing.freshness import RepairFreshnessLifecycle
from leadfinder.healing.memory import RepairMemory
from leadfinder.healing.multi_page import MultiPageRepairValidator
from leadfinder.healing.observability import RepairObservability, RepairSessionTelemetry
from leadfinder.healing.planner import HealingPlanner
from leadfinder.healing.schemas import (
    RepairConfidenceLevel,
    RepairEvaluation,
    RepairFreshnessStatus,
    RepairMemoryRecord,
    RepairPlan,
    RepairType,
)
from leadfinder.healing.semantic_memory import SemanticRepairMemory
from leadfinder.models.schemas import ScrapingTask
from leadfinder.validation.engine import ValidationEngine
from leadfinder.validation.schemas import ValidationResult

logger = get_logger("HEALING_ENGINE")


class HealingEngine:
    """Autonomous Self-Healing Engine coordinating evidence collection, candidate ranking, canary execution, deterministic evaluation, multi-page validation, and repair memory."""

    def __init__(
        self,
        evidence_collector: RepairEvidenceCollector | None = None,
        planner: HealingPlanner | None = None,
        executor: RepairExecutor | None = None,
        evaluator: RepairEvaluator | None = None,
        memory: RepairMemory | None = None,
        extraction_engine: ExtractionEngine | None = None,
        validation_engine: ValidationEngine | None = None,
        multi_page_validator: MultiPageRepairValidator | None = None,
        failed_memory: FailedRepairMemory | None = None,
        observability: RepairObservability | None = None,
        semantic_memory: SemanticRepairMemory | None = None,
        fingerprinter: DOMFingerprinter | None = None,
        freshness: RepairFreshnessLifecycle | None = None,
        action_executor: ActionRepairExecutor | None = None,
        max_repair_attempts: int = 3,
    ) -> None:
        self.evidence_collector = evidence_collector or RepairEvidenceCollector()
        self.planner = planner or HealingPlanner()
        self.executor = executor or RepairExecutor()
        self.evaluator = evaluator or RepairEvaluator()
        self.memory = memory or RepairMemory()
        self.extraction_engine = extraction_engine or ExtractionEngine()
        self.validation_engine = validation_engine or ValidationEngine()
        self.multi_page_validator = multi_page_validator or MultiPageRepairValidator(
            extraction_engine=self.extraction_engine,
            validation_engine=self.validation_engine,
        )
        self.failed_memory = failed_memory or FailedRepairMemory()
        self.observability = observability or RepairObservability()
        self.semantic_memory = semantic_memory or SemanticRepairMemory()
        self.fingerprinter = fingerprinter or DOMFingerprinter()
        self.freshness = freshness or RepairFreshnessLifecycle(
            fingerprinter=self.fingerprinter
        )
        self.action_executor = action_executor or ActionRepairExecutor()
        self.max_repair_attempts = max_repair_attempts

    async def heal(
        self,
        task: ScrapingTask,
        diagnosis: DiagnosisResult,
        validation: ValidationResult,
        current_schema: ExtractionSchema,
        scraper_config: dict[str, Any] | None = None,
        raw_results: list[dict[str, Any]] | None = None,
    ) -> tuple[
        bool,
        ExtractionSchema | None,
        RepairEvaluation,
        list[dict[str, Any]],
        list[dict[str, Any]],
    ]:
        """Execute autonomous self-healing loop with multi-page verification, confidence gating, and failed candidate learning:

        Returns:
            (success, healed_schema, final_evaluation, extracted_records, repair_history)
        """
        task_id = task.task_id
        start_time = time.time()
        logger.debug(
            f"Starting self-healing loop for task_id={task_id} (root_cause={diagnosis.root_cause.value})"
        )

        repair_history: list[dict[str, Any]] = []
        target_url = task.target_urls[0] if task.target_urls else "https://example.com"
        domain = urlparse(target_url).netloc.lower()

        # Step 1: Collect fresh live page evidence & check for transient recovery
        (
            raw_pages,
            is_recovered,
            recovery_val,
        ) = await self.evidence_collector.check_transient_recovery(
            task=task,
            schema=current_schema,
        )

        if not raw_pages and raw_results:
            raw_pages = [RawPage(**r) for r in raw_results]

        sample_html = raw_pages[0].get_primary_content() if raw_pages else ""
        current_fp = (
            self.fingerprinter.generate_fingerprint(sample_html)
            if sample_html
            else None
        )

        if is_recovered and recovery_val:
            logger.debug(f"Task {task_id} recovered transiently without repair needed.")
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

            ext_call = self.extraction_engine.extract(
                raw_results=[p.model_dump() for p in raw_pages],
                task=task,
                schema=current_schema,
            )
            ext_res = await ext_call if hasattr(ext_call, "__await__") else ext_call

            repair_history.append(
                {
                    "attempt": 1,
                    "repair_type": RepairType.NO_REPAIR_REQUIRED.value,
                    "confidence": 1.0,
                    "health_before": validation.health_score,
                    "health_after": recovery_val.health_score,
                    "accepted": True,
                }
            )

            # Record telemetry
            self.observability.record_session(
                RepairSessionTelemetry(
                    task_id=task_id,
                    domain=domain,
                    root_cause=diagnosis.root_cause.value,
                    initial_health=validation.health_score,
                    final_health=recovery_val.health_score,
                    improvement=recovery_val.health_score - validation.health_score,
                    attempts_count=1,
                    accepted=True,
                    persisted=False,
                    confidence_level=eval_res.confidence_level.value,
                    confidence_score=eval_res.confidence_score,
                    duration_ms=(time.time() - start_time) * 1000.0,
                )
            )
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
            logger.warning(
                f"No repair candidates could be generated for task {task_id}."
            )
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
            self.observability.record_session(
                RepairSessionTelemetry(
                    task_id=task_id,
                    domain=domain,
                    root_cause=diagnosis.root_cause.value,
                    initial_health=validation.health_score,
                    final_health=validation.health_score,
                    improvement=0.0,
                    accepted=False,
                    persisted=False,
                    rejection_reason="No viable repair candidates generated",
                    duration_ms=(time.time() - start_time) * 1000.0,
                )
            )
            return False, None, fallback_eval, [], repair_history

        # Step 3: Bounded repair candidate execution and canary validation
        attempts_budget = min(len(candidates), self.max_repair_attempts)
        last_eval: RepairEvaluation | None = None

        sig = self.memory.generate_signature(
            url=target_url,
            html=sample_html,
            fields=[f.name for f in current_schema.fields],
        )

        for attempt_idx in range(attempts_budget):
            candidate = candidates[attempt_idx]
            plan = candidate.plan
            attempt_num = attempt_idx + 1

            logger.debug(
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
            ext_call = self.extraction_engine.extract(
                raw_results=raw_dicts,
                task=task,
                schema=candidate_schema,
            )
            canary_extraction = (
                await ext_call if hasattr(ext_call, "__await__") else ext_call
            )

            # Canary validation: validate extracted records
            val_call = self.validation_engine.validate(
                extracted_results=canary_extraction.records,
                task=task,
                raw_results=raw_dicts,
            )
            canary_validation = (
                await val_call if hasattr(val_call, "__await__") else val_call
            )

            # Step 3b: Multi-Page Canary Validation (if enabled and multiple pages available)
            (
                mp_passed,
                mp_score,
                mp_metrics,
                mp_reason,
            ) = await self.multi_page_validator.validate_candidate_across_pages(
                task=task,
                schema=candidate_schema,
                raw_pages=raw_pages,
            )

            # Deterministic repair evaluation
            evaluation = self.evaluator.evaluate(
                before=validation,
                after=canary_validation,
                diagnosis=diagnosis,
                plan=plan,
                strategy_used=canary_extraction.strategy_used,
                multi_page_score=mp_score,
                multi_page_results=mp_metrics,
                attempt_number=attempt_num,
                target_fields=task.fields,
            )

            if not mp_passed and mp_reason:
                evaluation.accepted = False
                evaluation.rejection_reason = mp_reason

            last_eval = evaluation

            attempt_record = {
                "attempt": attempt_num,
                "repair_type": plan.repair_type.value,
                "confidence": plan.confidence,
                "health_before": validation.health_score,
                "health_after": canary_validation.health_score,
                "accepted": evaluation.accepted,
                "rejection_reason": evaluation.rejection_reason,
                "confidence_tier": evaluation.confidence_level.value,
            }
            repair_history.append(attempt_record)

            if evaluation.accepted:
                logger.debug(
                    f"Candidate repair accepted for task_id={task_id} on attempt {attempt_num}! "
                    f"health: {validation.health_score:.2f} -> {canary_validation.health_score:.2f} "
                    f"tier: {evaluation.confidence_level.value}"
                )

                # Persist to memory based on confidence tier
                persisted = False
                if evaluation.confidence_level in (
                    RepairConfidenceLevel.HIGH,
                    RepairConfidenceLevel.MEDIUM,
                ):
                    fresh_status = (
                        RepairFreshnessStatus.ACTIVE
                        if evaluation.confidence_level == RepairConfidenceLevel.HIGH
                        else RepairFreshnessStatus.PROBATION
                    )
                    rec = RepairMemoryRecord(
                        domain=domain,
                        signature=sig,
                        root_cause=diagnosis.root_cause.value,
                        repair_type=plan.repair_type,
                        successful_patch=plan.proposed_configuration,
                        health_before=validation.health_score,
                        health_after=canary_validation.health_score,
                        strategy=canary_extraction.strategy_used,
                        status=fresh_status,
                        confidence_level=evaluation.confidence_level,
                        structural_fingerprint=json.dumps(current_fp)
                        if current_fp
                        else None,
                    )
                    self.memory.record_success(rec)
                    if sample_html:
                        self.semantic_memory.register_record(rec, sample_html)
                    persisted = True

                # Record Telemetry Session
                self.observability.record_session(
                    RepairSessionTelemetry(
                        task_id=task_id,
                        domain=domain,
                        root_cause=diagnosis.root_cause.value,
                        initial_health=validation.health_score,
                        final_health=canary_validation.health_score,
                        improvement=canary_validation.health_score
                        - validation.health_score,
                        attempts_count=attempt_num,
                        candidates_generated=len(candidates),
                        multi_page_evaluated=evaluation.multi_page_evaluated,
                        multi_page_count=len(mp_metrics),
                        confidence_score=evaluation.confidence_score,
                        confidence_level=evaluation.confidence_level.value,
                        accepted=True,
                        persisted=persisted,
                        duration_ms=(time.time() - start_time) * 1000.0,
                    )
                )
                return (
                    True,
                    candidate_schema,
                    evaluation,
                    canary_extraction.records,
                    repair_history,
                )

            # If rejected, record candidate failure in failed repair memory
            logger.warning(
                f"Candidate repair rejected on attempt {attempt_num}: {evaluation.rejection_reason}"
            )
            self.failed_memory.record_failure(
                domain=domain,
                signature=sig,
                config=plan.proposed_configuration,
                reason=evaluation.rejection_reason or "Validation rejected",
            )

        # All attempts exhausted
        logger.error(
            f"Self-healing exhausted {attempts_budget} attempt(s) for task_id={task_id}. Escalating."
        )
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

        # Record Telemetry Session on Exhaustion
        self.observability.record_session(
            RepairSessionTelemetry(
                task_id=task_id,
                domain=domain,
                root_cause=diagnosis.root_cause.value,
                initial_health=validation.health_score,
                final_health=validation.health_score,
                improvement=0.0,
                attempts_count=attempts_budget,
                candidates_generated=len(candidates),
                accepted=False,
                persisted=False,
                rejection_reason=last_eval.rejection_reason,
                duration_ms=(time.time() - start_time) * 1000.0,
            )
        )
        return False, None, last_eval, [], repair_history
