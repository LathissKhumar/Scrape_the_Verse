"""Evidence-grounded repair planner that synthesizes, scores, and ranks candidate repair plans."""

import json
import re
from typing import Any
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from leadfinder.config.logging import get_logger
from leadfinder.diagnosis.schemas import DiagnosisResult, RootCause
from leadfinder.extraction.schema import (
    ExtractionSchema,
    ExtractionStrategyEnum,
    RawPage,
)
from leadfinder.healing.actions.detector import ActionIssueDetector
from leadfinder.healing.actions.planner import ActionRepairPlanner
from leadfinder.healing.failed_memory import FailedRepairMemory
from leadfinder.healing.fingerprint import DOMFingerprinter
from leadfinder.healing.memory import RepairMemory
from leadfinder.healing.schemas import RepairCandidate, RepairPlan, RepairType
from leadfinder.healing.semantic_memory import SemanticRepairMemory
from leadfinder.llm.base import LLMClient
from leadfinder.llm.ollama_client import clean_markdown_fences
from leadfinder.models.schemas import ScrapingTask
from leadfinder.validation.schemas import ValidationResult

logger = get_logger("HEALING_PLANNER")

HEALING_SYSTEM_PROMPT = """You are an autonomous scraper repair planner.
The scraper has already failed validation.
Your task is NOT to claim that it is fixed.
Your task is to propose the smallest evidence-supported repair.

You receive:
* user scraping task
* expected schema
* validation metrics
* diagnosis
* relevant raw page HTML/DOM evidence
* previous extraction configuration

Rules:
1. Never invent selectors.
2. Only propose selectors supported by observed DOM/content evidence.
3. Preserve fields that are currently working.
4. Repair only affected components.
5. Prefer deterministic extraction over LLM extraction.
6. Use semantic extraction when structural selectors are unstable.
7. Use LLM extraction only when deterministic methods are insufficient.
8. Do not modify unrelated configuration.
9. Produce a structured JSON repair plan.
10. Include expected validation criteria.
11. If evidence is insufficient, return ESCALATE.
12. Never claim the repair succeeded.

Output MUST be a single JSON object matching this schema:
{
  "repair_type": "REPAIR_CSS_SELECTORS",
  "target_component": "extraction",
  "affected_fields": ["field1"],
  "proposed_configuration": {"field1": ".new-selector"},
  "patch": {"fields": [{"name": "field1", "selector": ".new-selector"}]},
  "reason": "explanation grounded in DOM evidence",
  "confidence": 0.90,
  "expected_improvement": {"field1_coverage": 0.90},
  "test_requirements": ["field1 coverage >= 0.85"],
  "risk_level": "low"
}
"""

_WHITESPACE_REGEX = re.compile(r"\s+")

_STRATEGY_RELIABILITY_MAP: dict[RepairType, float] = {
    RepairType.REPAIR_CSS_SELECTORS: 0.90,
    RepairType.REPAIR_XPATH_SELECTORS: 0.85,
    RepairType.REPAIR_TABLE_SCHEMA: 0.85,
    RepairType.REPAIR_REGEX_PATTERN: 0.80,
    RepairType.REPAIR_ACTION_PLAN: 0.80,
    RepairType.REPAIR_CRAWLER_CONFIG: 0.75,
    RepairType.SWITCH_EXTRACTION_STRATEGY: 0.75,
    RepairType.REPAIR_SEMANTIC_FILTER: 0.75,
    RepairType.REPAIR_CHUNKING: 0.70,
    RepairType.REPAIR_LLM_EXTRACTION_SCHEMA: 0.70,
    RepairType.REPAIR_SCRAPER_CONFIG: 0.65,
    RepairType.BRIGHTDATA_REFACTOR_FALLBACK: 0.60,
    RepairType.NO_REPAIR_REQUIRED: 1.0,
    RepairType.ESCALATE: 0.10,
}


class HealingPlanner:
    """Evidence-grounded repair planner that synthesizes, scores, and ranks candidate repair plans."""

    def __init__(
        self,
        llm_client: LLMClient | None = None,
        memory: RepairMemory | None = None,
        failed_memory: FailedRepairMemory | None = None,
        semantic_memory: SemanticRepairMemory | None = None,
        action_detector: ActionIssueDetector | None = None,
        action_planner: ActionRepairPlanner | None = None,
        fingerprinter: DOMFingerprinter | None = None,
        confidence_weight: float = 0.35,
        improvement_weight: float = 0.30,
        reliability_weight: float = 0.20,
        history_weight: float = 0.10,
        risk_weight: float = 0.05,
    ) -> None:
        self.llm_client = llm_client
        self.memory = memory or RepairMemory()
        self.failed_memory = failed_memory or FailedRepairMemory()
        self.semantic_memory = semantic_memory or SemanticRepairMemory()
        self.action_detector = action_detector or ActionIssueDetector()
        self.action_planner = action_planner or ActionRepairPlanner(
            llm_client=llm_client
        )
        self.fingerprinter = fingerprinter or DOMFingerprinter()
        self.confidence_weight = confidence_weight
        self.improvement_weight = improvement_weight
        self.reliability_weight = reliability_weight
        self.history_weight = history_weight
        self.risk_weight = risk_weight

    def score_candidate(
        self,
        plan: RepairPlan,
        diagnosis: DiagnosisResult,
        source: str = "planner_llm",
        domain: str = "",
        signature: str = "",
    ) -> float:
        """Calculate Crawl4AI-inspired adaptive candidate score with failed candidate penalty."""
        conf = plan.confidence

        # Expected improvement estimate
        exp_imp = 0.5
        if plan.expected_improvement:
            exp_imp = sum(plan.expected_improvement.values()) / max(
                len(plan.expected_improvement), 1
            )

        strat_rel = _STRATEGY_RELIABILITY_MAP.get(plan.repair_type, 0.50)

        # Historical success
        hist_score = (
            1.0 if source == "memory" else (0.8 if source == "semantic_memory" else 0.5)
        )

        # Risk factor
        risk_penalty = (
            0.1
            if plan.risk_level == "low"
            else (0.5 if plan.risk_level == "medium" else 1.0)
        )

        # Failed candidate penalty
        fail_penalty = (
            self.failed_memory.get_penalty(
                domain, signature, plan.proposed_configuration
            )
            if domain and signature
            else 0.0
        )

        score = (
            (self.confidence_weight * conf)
            + (self.improvement_weight * exp_imp)
            + (self.reliability_weight * strat_rel)
            + (self.history_weight * hist_score)
            - (self.risk_weight * risk_penalty)
            - fail_penalty
        )
        return max(0.0, min(1.0, score))

    async def generate_candidates(
        self,
        task: ScrapingTask,
        diagnosis: DiagnosisResult,
        validation: ValidationResult,
        raw_pages: list[RawPage],
        current_schema: ExtractionSchema,
        failed_attempts: list[dict[str, Any]] | None = None,
    ) -> list[RepairCandidate]:
        """Generate, score, and rank repair candidates using memory, actions, LLM, and deterministic heuristics."""
        logger.debug(
            f"Generating repair candidates for task_id={task.task_id} (root_cause={diagnosis.root_cause.value})"
        )
        candidates: list[RepairCandidate] = []
        target_url = task.target_urls[0] if task.target_urls else "https://example.com"
        parsed = urlparse(target_url)
        domain = parsed.netloc.lower()

        sample_html = raw_pages[0].get_primary_content() if raw_pages else ""
        field_names = [f.name for f in current_schema.fields]
        sig = self.memory.generate_signature(
            url=target_url, html=sample_html, fields=field_names
        )

        # 1. Check Exact Memory for previously successful repairs on same domain/signature
        memory_records = self.memory.find_similar_repairs(
            domain=domain, signature=sig, root_cause=diagnosis.root_cause.value
        )
        for mem in memory_records:
            if not self.failed_memory.is_suppressed(domain, sig, mem.successful_patch):
                mem_plan = RepairPlan(
                    repair_type=mem.repair_type,
                    target_component="extraction",
                    affected_fields=diagnosis.affected_fields or field_names,
                    previous_configuration=current_schema.model_dump(),
                    proposed_configuration=mem.successful_patch,
                    patch={
                        "fields": [
                            {"name": k, "selector": v}
                            for k, v in mem.successful_patch.items()
                        ]
                    },
                    reason=f"Reused successful pattern from memory for {mem.domain} ({mem.signature})",
                    confidence=0.92,
                    expected_improvement={"coverage": 0.90},
                    risk_level="low",
                    level=1,
                )
                score = self.score_candidate(
                    plan=mem_plan,
                    diagnosis=diagnosis,
                    source="memory",
                    domain=domain,
                    signature=sig,
                )
                candidates.append(
                    RepairCandidate(plan=mem_plan, score=score, source="memory")
                )

        # 2. Check Dynamic UI Action Issues (Cookie banner, blocking modal, load-more triggers)
        if sample_html:
            detected_issues = self.action_detector.detect_blocking_issues(sample_html)
            if detected_issues:
                action_plans = self.action_planner.plan_from_issues(
                    detected_issues, task
                )
                for a_plan in action_plans:
                    act_repair_plan = RepairPlan(
                        repair_type=RepairType.REPAIR_ACTION_PLAN,
                        target_component="scraper",
                        proposed_configuration={"action_plan": a_plan.model_dump()},
                        patch={"action_plan": a_plan.model_dump()},
                        reason=f"UI interaction barrier detected: {a_plan.description}",
                        confidence=0.85,
                        expected_improvement={"coverage": 0.90},
                        risk_level="low",
                        level=2,
                    )
                    if not self.failed_memory.is_suppressed(
                        domain, sig, act_repair_plan.proposed_configuration
                    ):
                        score = self.score_candidate(
                            plan=act_repair_plan,
                            diagnosis=diagnosis,
                            source="action_detector",
                            domain=domain,
                            signature=sig,
                        )
                        candidates.append(
                            RepairCandidate(
                                plan=act_repair_plan,
                                score=score,
                                source="action_detector",
                            )
                        )

        # 3. Check Cross-Domain Semantic Memory for structural pattern transfers
        if sample_html:
            semantic_matches = self.semantic_memory.find_cross_domain_candidates(
                sample_html, field_names
            )
            for smem in semantic_matches:
                if not self.failed_memory.is_suppressed(
                    domain, sig, smem.successful_patch
                ):
                    smem_plan = RepairPlan(
                        repair_type=smem.repair_type,
                        target_component="extraction",
                        affected_fields=field_names,
                        proposed_configuration=smem.successful_patch,
                        patch={
                            "fields": [
                                {"name": k, "selector": v}
                                for k, v in smem.successful_patch.items()
                            ]
                        },
                        reason=f"Cross-domain structural pattern transferred from {smem.domain}",
                        confidence=0.78,
                        expected_improvement={"coverage": 0.85},
                        risk_level="medium",
                        level=1,
                    )
                    score = self.score_candidate(
                        plan=smem_plan,
                        diagnosis=diagnosis,
                        source="semantic_memory",
                        domain=domain,
                        signature=sig,
                    )
                    candidates.append(
                        RepairCandidate(
                            plan=smem_plan, score=score, source="semantic_memory"
                        )
                    )

        # 4. Invoke LLM for evidence-grounded candidate generation
        if self.llm_client and sample_html:
            llm_candidate = await self._generate_llm_candidate(
                task=task,
                diagnosis=diagnosis,
                validation=validation,
                sample_html=sample_html,
                current_schema=current_schema,
                failed_attempts=failed_attempts,
            )
            if llm_candidate and not self.failed_memory.is_suppressed(
                domain, sig, llm_candidate.proposed_configuration
            ):
                score = self.score_candidate(
                    plan=llm_candidate,
                    diagnosis=diagnosis,
                    source="planner_llm",
                    domain=domain,
                    signature=sig,
                )
                candidates.append(
                    RepairCandidate(
                        plan=llm_candidate, score=score, source="planner_llm"
                    )
                )

        # 5. Deterministic Heuristics & Alternative Candidates
        deterministic_candidates = self._generate_deterministic_candidates(
            diagnosis=diagnosis,
            current_schema=current_schema,
            raw_pages=raw_pages,
        )
        for d_plan in deterministic_candidates:
            if not self.failed_memory.is_suppressed(
                domain, sig, d_plan.proposed_configuration
            ):
                score = self.score_candidate(
                    plan=d_plan,
                    diagnosis=diagnosis,
                    source="deterministic",
                    domain=domain,
                    signature=sig,
                )
                candidates.append(
                    RepairCandidate(plan=d_plan, score=score, source="deterministic")
                )

        # Ensure at least one candidate (fallback to strategy switch or escalate)
        if not candidates:
            fallback_plan = RepairPlan(
                repair_type=RepairType.SWITCH_EXTRACTION_STRATEGY,
                target_component="extraction",
                proposed_configuration={"strategy": "semantic"},
                patch={"strategy": "semantic"},
                reason="Fallback to semantic extraction strategy",
                confidence=0.70,
                level=1,
            )
            score = self.score_candidate(
                plan=fallback_plan,
                diagnosis=diagnosis,
                source="fallback",
                domain=domain,
                signature=sig,
            )
            candidates.append(
                RepairCandidate(plan=fallback_plan, score=score, source="fallback")
            )

        # Deduplicate and sort descending by score
        unique_candidates: list[RepairCandidate] = []
        seen_types: set[str] = set()
        for candidate_item in sorted(candidates, key=lambda x: x.score, reverse=True):
            rep_key = f"{candidate_item.plan.repair_type.value}:{json.dumps(candidate_item.plan.proposed_configuration, sort_keys=True)}"
            if rep_key not in seen_types:
                seen_types.add(rep_key)
                unique_candidates.append(candidate_item)

        for idx, candidate_item in enumerate(unique_candidates, start=1):
            candidate_item.rank = idx

        return unique_candidates

    async def _generate_llm_candidate(
        self,
        task: ScrapingTask,
        diagnosis: DiagnosisResult,
        validation: ValidationResult,
        sample_html: str,
        current_schema: ExtractionSchema,
        failed_attempts: list[dict[str, Any]] | None = None,
    ) -> RepairPlan | None:
        """Query Qwen3:8b with a clean, script-free HTML snippet and diagnostic context to produce a structured RepairPlan."""
        try:
            # Clean HTML to keep prompt lightweight and fast for local Ollama
            soup = BeautifulSoup(sample_html, "html.parser")
            for tag in soup(
                [
                    "script",
                    "style",
                    "noscript",
                    "svg",
                    "path",
                    "link",
                    "meta",
                    "header",
                    "footer",
                    "nav",
                ]
            ):
                tag.decompose()

            # Find main content container or body
            main_container = (
                soup.find("main") or soup.find("article") or soup.body or soup
            )
            raw_snippet = str(main_container) if main_container else str(soup)
            clean_snippet = _WHITESPACE_REGEX.sub(" ", raw_snippet)[:1200]

            user_prompt = f"""Target Objective: {task.objective}
Target URLs: {task.target_urls}
Current Extraction Strategy: {current_schema.strategy.value}
Current Base Selector: {current_schema.base_selector}
Current Field Rules: {[f.model_dump() for f in current_schema.fields]}

Validation Status: {validation.status} (Health Score: {validation.health_score:.2f})
Validation Failures: {[f.model_dump() for f in validation.failures]}

Diagnosis Root Cause: {diagnosis.root_cause.value} (Confidence: {diagnosis.confidence:.2f})
Affected Fields: {diagnosis.affected_fields}
Diagnostic Evidence: {diagnosis.evidence}
Recommended Strategy: {diagnosis.repair_strategy.value}

Previous Failed Repair Attempts: {failed_attempts or []}

Observed Clean HTML DOM Snippet:
```html
{clean_snippet}
```

Propose the smallest evidence-supported repair plan in strict JSON. Do NOT invent selectors not present in the HTML snippet.
"""
            raw_response = await self.llm_client.invoke(
                system_prompt=HEALING_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                json_mode=True,
            )
            cleaned = clean_markdown_fences(raw_response)
            data = json.loads(cleaned)

            # Validate repair_type
            rep_type_str = data.get("repair_type", "REPAIR_CSS_SELECTORS")
            try:
                rep_type = RepairType(rep_type_str)
            except ValueError:
                rep_type = RepairType.REPAIR_CSS_SELECTORS

            # Sanitize target_component to valid Literal["extraction", "scraper", "collector"]
            raw_target = str(data.get("target_component", "extraction")).lower()
            if any(
                k in raw_target
                for k in [
                    "scraper",
                    "crawler",
                    "browser",
                    "content",
                    "availability",
                    "page",
                ]
            ):
                target_component = "scraper"
            elif any(
                k in raw_target for k in ["collector", "network", "proxy", "brightdata"]
            ):
                target_component = "collector"
            else:
                target_component = "extraction"

            # Sanitize risk_level to valid Literal["low", "medium", "high"]
            raw_risk = str(data.get("risk_level", "low")).lower()
            if any(k in raw_risk for k in ["critical", "severe", "high"]):
                risk_level = "high"
            elif any(k in raw_risk for k in ["medium", "moderate"]):
                risk_level = "medium"
            else:
                risk_level = "low"

            raw_confidence = data.get("confidence", 0.85)
            try:
                conf_val = max(0.0, min(1.0, float(raw_confidence)))
            except (ValueError, TypeError):
                conf_val = 0.85

            return RepairPlan(
                repair_type=rep_type,
                target_component=target_component,
                affected_fields=data.get("affected_fields", diagnosis.affected_fields),
                previous_configuration=current_schema.model_dump(),
                proposed_configuration=data.get("proposed_configuration", {})
                if isinstance(data.get("proposed_configuration"), dict)
                else {},
                patch=data.get("patch", {})
                if isinstance(data.get("patch"), dict)
                else {},
                reason=data.get("reason", "LLM proposed evidence-based repair"),
                confidence=conf_val,
                expected_improvement=data.get("expected_improvement", {"coverage": 0.9})
                if isinstance(data.get("expected_improvement"), dict)
                else {"coverage": 0.9},
                test_requirements=data.get("test_requirements", [])
                if isinstance(data.get("test_requirements"), list)
                else [],
                risk_level=risk_level,
                level=1,
            )
        except Exception as error:
            logger.warning(f"Failed to generate LLM repair candidate: {error}")
            return None

    def _generate_deterministic_candidates(
        self,
        diagnosis: DiagnosisResult,
        current_schema: ExtractionSchema,
        raw_pages: list[RawPage],
    ) -> list[RepairPlan]:
        """Generate deterministic heuristic repair plans for common standard failures."""
        candidates: list[RepairPlan] = []

        # If CSS, Regex, or XPath failed and raw page text is present -> offer strategy switch to LLM or Semantic
        if diagnosis.root_cause in (
            RootCause.SELECTOR_DRIFT,
            RootCause.DOM_STRUCTURE_CHANGE,
            RootCause.EXTRACTION_DEGRADATION,
        ):
            if current_schema.strategy in (
                ExtractionStrategyEnum.CSS,
                ExtractionStrategyEnum.REGEX,
            ):
                # Candidate 1: Switch to LLM chunking (high fidelity)
                candidates.append(
                    RepairPlan(
                        repair_type=RepairType.SWITCH_EXTRACTION_STRATEGY,
                        target_component="extraction",
                        previous_configuration={
                            "strategy": current_schema.strategy.value
                        },
                        proposed_configuration={"strategy": "llm"},
                        patch={"strategy": "llm"},
                        reason="Selectors or regex drifted; switch to LLM chunking extraction",
                        confidence=0.85,
                        expected_improvement={"coverage": 0.90},
                        risk_level="low",
                        level=1,
                    )
                )
                # Candidate 2: Switch to semantic
                candidates.append(
                    RepairPlan(
                        repair_type=RepairType.SWITCH_EXTRACTION_STRATEGY,
                        target_component="extraction",
                        previous_configuration={
                            "strategy": current_schema.strategy.value
                        },
                        proposed_configuration={"strategy": "semantic"},
                        patch={"strategy": "semantic"},
                        reason="Selectors drifted; switch to semantic extraction",
                        confidence=0.75,
                        expected_improvement={"coverage": 0.80},
                        risk_level="low",
                        level=1,
                    )
                )

        # Table structure change -> offer table schema repair
        if diagnosis.root_cause == RootCause.TABLE_STRUCTURE_CHANGE:
            candidates.append(
                RepairPlan(
                    repair_type=RepairType.REPAIR_TABLE_SCHEMA,
                    target_component="extraction",
                    proposed_configuration={"strategy": "table"},
                    patch={"strategy": "table"},
                    reason="Switch to robust HTML table extraction mode",
                    confidence=0.85,
                    level=1,
                )
            )

        return candidates
