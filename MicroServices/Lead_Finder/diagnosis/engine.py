import json
from typing import Any

from leadfinder.config.logging import get_logger
from leadfinder.diagnosis.classifier import RuleBasedClassifier
from leadfinder.diagnosis.evidence import DiagnosisEvidenceBuilder
from leadfinder.diagnosis.prompt import DIAGNOSIS_SYSTEM_PROMPT, build_diagnosis_prompt
from leadfinder.diagnosis.schemas import (
    AffectedStage,
    DiagnosisResult,
    RecommendedAction,
    RepairStrategy,
    RootCause,
)
from leadfinder.llm.base import LLMClient
from leadfinder.llm.ollama_client import clean_markdown_fences
from leadfinder.models.schemas import ScrapingTask
from leadfinder.validation.schemas import ValidationResult

logger = get_logger("DIAGNOSIS_ENGINE")


class DiagnosisEngine:
    """Orchestrates deterministic rule-based and LLM-assisted failure diagnosis."""

    def __init__(
        self,
        llm_client: LLMClient | None = None,
        evidence_builder: DiagnosisEvidenceBuilder | None = None,
        rule_classifier: RuleBasedClassifier | None = None,
    ):
        self.llm_client = llm_client
        self.evidence_builder = evidence_builder or DiagnosisEvidenceBuilder()
        self.rule_classifier = rule_classifier or RuleBasedClassifier()

    def _parse_llm_diagnosis(
        self, raw_output: str, evidence: dict[str, Any]
    ) -> DiagnosisResult:
        """Parse and validate LLM output into a typed DiagnosisResult."""
        cleaned = clean_markdown_fences(raw_output).strip()
        if not cleaned:
            return DiagnosisResult(
                diagnosis_status="inconclusive",
                root_cause=RootCause.UNKNOWN,
                confidence=0.3,
                evidence=["Empty response received from LLM diagnosis."],
                repair_strategy=RepairStrategy.ESCALATE,
            )

        try:
            parsed = json.loads(cleaned)
            # Normalize root_cause
            rc_str = str(parsed.get("root_cause", "UNKNOWN")).upper()
            root_cause = (
                RootCause[rc_str]
                if rc_str in RootCause.__members__
                else RootCause.UNKNOWN
            )

            # Normalize stage
            st_str = str(parsed.get("affected_stage", "unknown")).lower()
            stage = (
                AffectedStage[st_str.upper()]
                if st_str.upper() in AffectedStage.__members__
                else AffectedStage.UNKNOWN
            )

            # Normalize repair strategy
            rs_str = str(parsed.get("repair_strategy", "ESCALATE")).upper()
            strategy = (
                RepairStrategy[rs_str]
                if rs_str in RepairStrategy.__members__
                else RepairStrategy.ESCALATE
            )

            # Normalize recommended action
            ra_str = str(parsed.get("recommended_action", "MANUAL_INSPECTION")).upper()
            action = (
                RecommendedAction[ra_str]
                if ra_str in RecommendedAction.__members__
                else RecommendedAction.MANUAL_INSPECTION
            )

            confidence = float(parsed.get("confidence", 0.7))

            return DiagnosisResult(
                diagnosis_status="diagnosed" if confidence >= 0.65 else "inconclusive",
                root_cause=root_cause,
                confidence=round(max(0.0, min(1.0, confidence)), 2),
                failure_category=str(
                    parsed.get("failure_category", "EXTRACTION_DEGRADATION")
                ),
                affected_stage=stage,
                affected_fields=parsed.get(
                    "affected_fields", evidence.get("affected_fields", [])
                ),
                evidence=parsed.get("evidence", []),
                repair_strategy=strategy,
                repair_targets=parsed.get("repair_targets", []),
                recommended_action=action,
                metadata={"raw_llm_diagnosis": True},
            )
        except Exception as e:
            logger.warning(f"Failed to parse LLM diagnosis JSON: {e}")
            return DiagnosisResult(
                diagnosis_status="inconclusive",
                root_cause=RootCause.UNKNOWN,
                confidence=0.3,
                evidence=[f"Failed to parse LLM diagnosis response: {e!s}"],
                repair_strategy=RepairStrategy.ESCALATE,
            )

    async def diagnose_async(
        self,
        task: ScrapingTask,
        validation_result: ValidationResult,
        raw_results: Any | None = None,
        extracted_results: list[dict[str, Any]] | None = None,
        scraper_metadata: dict[str, Any] | None = None,
    ) -> DiagnosisResult:
        """Asynchronously diagnose failure cause and determine adaptive repair strategy."""
        logger.debug(
            f"task_id={task.task_id} Initiating failure diagnosis (validation_status={validation_result.status})"
        )

        # 1. Assemble compact evidence
        evidence = self.evidence_builder.build_evidence(
            task=task,
            validation_result=validation_result,
            raw_results=raw_results,
            extracted_results=extracted_results,
            scraper_metadata=scraper_metadata,
        )

        # 2. Try Deterministic Rule-Based Classification first
        rule_result = self.rule_classifier.classify(
            evidence=evidence, validation_result=validation_result
        )
        if rule_result:
            logger.debug(
                f"task_id={task.task_id} Deterministic rule classified root_cause='{rule_result.root_cause.value}' (confidence={rule_result.confidence})"
            )
            return rule_result

        # 3. If ambiguous, invoke LLM (Qwen3:8b)
        if self.llm_client:
            prompt = build_diagnosis_prompt(evidence)
            try:
                raw_response = await self.llm_client.invoke(
                    prompt=prompt,
                    system=DIAGNOSIS_SYSTEM_PROMPT,
                    json_mode=True,
                )
                diagnosis = self._parse_llm_diagnosis(raw_response, evidence)
                logger.debug(
                    f"task_id={task.task_id} LLM diagnosed root_cause='{diagnosis.root_cause.value}' (confidence={diagnosis.confidence})"
                )
                return diagnosis
            except Exception as e:
                logger.error(
                    f"task_id={task.task_id} LLM diagnosis execution error: {e}"
                )

        # Fallback inconclusive result
        return DiagnosisResult(
            diagnosis_status="inconclusive",
            root_cause=RootCause.UNKNOWN,
            confidence=0.4,
            failure_category="UNKNOWN",
            affected_stage=AffectedStage.UNKNOWN,
            affected_fields=evidence.get("affected_fields", []),
            evidence=[
                "Ambiguous failure metrics without definitive rule or LLM diagnosis."
            ],
            repair_strategy=RepairStrategy.ESCALATE,
            recommended_action=RecommendedAction.MANUAL_INSPECTION,
        )
