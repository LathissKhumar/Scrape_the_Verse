import json
from typing import Any, Optional
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from app.config.logging import get_logger
from app.diagnosis.schemas import DiagnosisResult, RepairStrategy, RootCause
from app.extraction.schema import ExtractionSchema, ExtractionStrategyEnum, RawPage
from app.healing.memory import RepairMemory
from app.healing.schemas import RepairCandidate, RepairPlan, RepairType
from app.llm.base import LLMClient
from app.llm.ollama_client import clean_markdown_fences
from app.models.schemas import ScrapingTask
from app.validation.schemas import ValidationResult

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


class HealingPlanner:
    """Evidence-grounded repair planner that synthesizes, scores, and ranks candidate repair plans."""

    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        memory: Optional[RepairMemory] = None,
        confidence_weight: float = 0.35,
        improvement_weight: float = 0.30,
        reliability_weight: float = 0.20,
        history_weight: float = 0.10,
        risk_weight: float = 0.05,
    ):
        self.llm_client = llm_client
        self.memory = memory or RepairMemory()
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
    ) -> float:
        """Calculate Crawl4AI-inspired adaptive candidate score."""
        conf = plan.confidence

        # Expected improvement estimate
        exp_imp = 0.5
        if plan.expected_improvement:
            exp_imp = sum(plan.expected_improvement.values()) / max(len(plan.expected_improvement), 1)

        # Strategy reliability
        strategy_reliability_map = {
            RepairType.REPAIR_CSS_SELECTORS: 0.90,
            RepairType.REPAIR_XPATH_SELECTORS: 0.85,
            RepairType.REPAIR_TABLE_SCHEMA: 0.85,
            RepairType.REPAIR_REGEX_PATTERN: 0.80,
            RepairType.SWITCH_EXTRACTION_STRATEGY: 0.75,
            RepairType.REPAIR_SEMANTIC_FILTER: 0.75,
            RepairType.REPAIR_CHUNKING: 0.70,
            RepairType.REPAIR_LLM_EXTRACTION_SCHEMA: 0.70,
            RepairType.REPAIR_SCRAPER_CONFIG: 0.65,
            RepairType.BRIGHTDATA_REFACTOR_FALLBACK: 0.60,
            RepairType.NO_REPAIR_REQUIRED: 1.0,
            RepairType.ESCALATE: 0.10,
        }
        strat_rel = strategy_reliability_map.get(plan.repair_type, 0.50)

        # Historical success
        hist_score = 1.0 if source == "memory" else 0.5

        # Risk factor
        risk_penalty = 0.1 if plan.risk_level == "low" else (0.5 if plan.risk_level == "medium" else 1.0)

        score = (
            (self.confidence_weight * conf)
            + (self.improvement_weight * exp_imp)
            + (self.reliability_weight * strat_rel)
            + (self.history_weight * hist_score)
            - (self.risk_weight * risk_penalty)
        )
        return max(0.0, min(1.0, score))

    async def generate_candidates(
        self,
        task: ScrapingTask,
        diagnosis: DiagnosisResult,
        validation: ValidationResult,
        raw_pages: list[RawPage],
        current_schema: ExtractionSchema,
        failed_attempts: Optional[list[dict[str, Any]]] = None,
    ) -> list[RepairCandidate]:
        """Generate, score, and rank repair candidates using memory, LLM, and deterministic heuristics."""
        logger.info(f"Generating repair candidates for task_id={task.task_id} (root_cause={diagnosis.root_cause.value})")
        candidates: list[RepairCandidate] = []
        target_url = task.target_urls[0] if task.target_urls else "https://example.com"
        parsed = urlparse(target_url)
        domain = parsed.netloc.lower()

        # 1. Check Memory for previously successful repairs on same domain/signature
        sample_html = raw_pages[0].get_primary_content() if raw_pages else ""
        field_names = [f.name for f in current_schema.fields]
        sig = self.memory.generate_signature(url=target_url, html=sample_html, fields=field_names)
        memory_records = self.memory.find_similar_repairs(domain=domain, signature=sig, root_cause=diagnosis.root_cause.value)

        for mem in memory_records:
            mem_plan = RepairPlan(
                repair_type=mem.repair_type,
                target_component="extraction",
                affected_fields=diagnosis.affected_fields or field_names,
                previous_configuration=current_schema.model_dump(),
                proposed_configuration=mem.successful_patch,
                patch={"fields": [{"name": k, "selector": v} for k, v in mem.successful_patch.items()]},
                reason=f"Reused successful pattern from memory for {mem.domain} ({mem.signature})",
                confidence=0.92,
                expected_improvement={"coverage": 0.90},
                risk_level="low",
                level=1,
            )
            score = self.score_candidate(plan=mem_plan, diagnosis=diagnosis, source="memory")
            candidates.append(RepairCandidate(plan=mem_plan, score=score, source="memory"))

        # 2. Invoke LLM for evidence-grounded candidate generation
        if self.llm_client and sample_html:
            llm_candidate = await self._generate_llm_candidate(
                task=task,
                diagnosis=diagnosis,
                validation=validation,
                sample_html=sample_html,
                current_schema=current_schema,
                failed_attempts=failed_attempts,
            )
            if llm_candidate:
                score = self.score_candidate(plan=llm_candidate, diagnosis=diagnosis, source="planner_llm")
                candidates.append(RepairCandidate(plan=llm_candidate, score=score, source="planner_llm"))

        # 3. Deterministic Heuristics & Alternative Candidates
        deterministic_candidates = self._generate_deterministic_candidates(
            diagnosis=diagnosis,
            current_schema=current_schema,
            raw_pages=raw_pages,
        )
        for d_plan in deterministic_candidates:
            score = self.score_candidate(plan=d_plan, diagnosis=diagnosis, source="deterministic")
            candidates.append(RepairCandidate(plan=d_plan, score=score, source="deterministic"))

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
            score = self.score_candidate(plan=fallback_plan, diagnosis=diagnosis, source="fallback")
            candidates.append(RepairCandidate(plan=fallback_plan, score=score, source="fallback"))

        # Deduplicate and sort descending by score
        unique_candidates: list[RepairCandidate] = []
        seen_types = set()
        for c in sorted(candidates, key=lambda x: x.score, reverse=True):
            rep_key = f"{c.plan.repair_type.value}:{json.dumps(c.plan.proposed_configuration, sort_keys=True)}"
            if rep_key not in seen_types:
                seen_types.add(rep_key)
                unique_candidates.append(c)

        for idx, c in enumerate(unique_candidates, start=1):
            c.rank = idx

        return unique_candidates

    async def _generate_llm_candidate(
        self,
        task: ScrapingTask,
        diagnosis: DiagnosisResult,
        validation: ValidationResult,
        sample_html: str,
        current_schema: ExtractionSchema,
        failed_attempts: Optional[list[dict[str, Any]]] = None,
    ) -> Optional[RepairPlan]:
        """Query Qwen3:8b with HTML snippet and diagnostic context to produce a structured RepairPlan."""
        try:
            # Extract clean DOM snippet
            soup = BeautifulSoup(sample_html[:8000], "html.parser")
            body = soup.body
            snippet = str(body)[:4000] if body else sample_html[:4000]

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

Observed Raw HTML DOM Snippet:
```html
{snippet}
```

Propose the smallest evidence-supported repair plan in strict JSON. Do NOT invent selectors not present in the HTML snippet.
"""
            raw_response = await self.llm_client.invoke(
                system_prompt=HEALING_SYSTEM_PROMPT,
                user_prompt=user_prompt,
            )
            cleaned = clean_markdown_fences(raw_response)
            data = json.loads(cleaned)

            # Validate repair_type
            rep_type_str = data.get("repair_type", "REPAIR_CSS_SELECTORS")
            try:
                rep_type = RepairType(rep_type_str)
            except ValueError:
                rep_type = RepairType.REPAIR_CSS_SELECTORS

            return RepairPlan(
                repair_type=rep_type,
                target_component=data.get("target_component", "extraction"),
                affected_fields=data.get("affected_fields", diagnosis.affected_fields),
                previous_configuration=current_schema.model_dump(),
                proposed_configuration=data.get("proposed_configuration", {}),
                patch=data.get("patch", {}),
                reason=data.get("reason", "LLM proposed evidence-based repair"),
                confidence=float(data.get("confidence", 0.85)),
                expected_improvement=data.get("expected_improvement", {"coverage": 0.9}),
                test_requirements=data.get("test_requirements", []),
                risk_level=data.get("risk_level", "low"),
                level=1,
            )
        except Exception as e:
            logger.warning(f"Failed to generate LLM repair candidate: {e}")
            return None

    def _generate_deterministic_candidates(
        self,
        diagnosis: DiagnosisResult,
        current_schema: ExtractionSchema,
        raw_pages: list[RawPage],
    ) -> list[RepairPlan]:
        """Generate deterministic heuristic repair plans for common standard failures."""
        candidates: list[RepairPlan] = []

        # If CSS or XPath failed and raw page text is present -> offer strategy switch to Semantic or LLM
        if diagnosis.root_cause in (RootCause.SELECTOR_DRIFT, RootCause.DOM_STRUCTURE_CHANGE, RootCause.EXTRACTION_DEGRADATION):
            if current_schema.strategy == ExtractionStrategyEnum.CSS:
                candidates.append(
                    RepairPlan(
                        repair_type=RepairType.SWITCH_EXTRACTION_STRATEGY,
                        target_component="extraction",
                        previous_configuration={"strategy": "css"},
                        proposed_configuration={"strategy": "semantic"},
                        patch={"strategy": "semantic"},
                        reason="CSS selectors drifted; switch to semantic + chunking extraction",
                        confidence=0.80,
                        expected_improvement={"coverage": 0.85},
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
