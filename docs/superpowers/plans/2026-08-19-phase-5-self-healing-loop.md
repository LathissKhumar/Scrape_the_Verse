# Phase 5: Autonomous Self-Healing Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement Phase 5 autonomous self-healing for scraping and extraction failures with fresh page acquisition, deterministic canary evaluation, multi-level repair hierarchy, Crawl4AI-inspired adaptive signals, and LangGraph feedback loop.

**Architecture:** A modular self-healing subsystem (`app/healing/`) coordinated with `ValidationEngine`, `DiagnosisAgent`, and `HealingAgent` via a bounded LangGraph feedback loop. Fresh DOM evidence is collected by `RepairEvidenceCollector`, candidate repairs are synthesized by `HealingPlanner` via local Qwen3:8b and ranked via adaptive scoring, applied safely by `RepairExecutor`, and tested deterministically by `RepairEvaluator`.

**Tech Stack:** Python 3.11+, LangGraph, FastAPI, Pydantic v2, Beautiful Soup 4, lxml, Ollama (Qwen3:8b), httpx, pytest, pytest-asyncio.

**Spec:** [`docs/superpowers/specs/2026-08-19-phase-5-self-healing-loop-design.md`](file:///c:/Projects/Scrape_the_Verse/docs/superpowers/specs/2026-08-19-phase-5-self-healing-loop-design.md)

## Global Constraints
- Do NOT install Crawl4AI as a runtime dependency.
- LLM model MUST be local `qwen3:8b` via existing `OllamaClient`.
- LLM NEVER approves its own repair; deterministic `RepairEvaluator` holds the gate.
- No arbitrary Python/JavaScript or shell execution from LLM outputs.
- Preserve all existing Phase 1–4 tests and functionality.

---

### Task 1: Healing Schemas & Data Models

**Files:**
- Create: `app/healing/__init__.py`
- Create: `app/healing/schemas.py`
- Test: `tests/test_healing_schema.py`

**Interfaces:**
- Produces: `RepairType`, `RepairStatus`, `PerformanceSnapshot`, `RepairPlan`, `RepairCandidate`, `RepairEvaluation`, `RepairMemoryRecord`

- [ ] **Step 1: Write the failing schema test**
Create `tests/test_healing_schema.py` validating `RepairType`, `RepairPlan`, `PerformanceSnapshot`, and `RepairEvaluation` instantiation and validation constraints.

- [ ] **Step 2: Run test to verify it fails**
Run: `python -m pytest tests/test_healing_schema.py -v`
Expected: FAIL (ModuleNotFoundError: No module named 'app.healing')

- [ ] **Step 3: Write implementation**
Create `app/healing/__init__.py` and `app/healing/schemas.py` defining Pydantic models and Enums.

- [ ] **Step 4: Run test to verify it passes**
Run: `python -m pytest tests/test_healing_schema.py -v`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add app/healing/__init__.py app/healing/schemas.py tests/test_healing_schema.py
git commit -m "feat(healing): add healing schemas and performance snapshot models"
```

---

### Task 2: Minimal-Patch Repair Patcher

**Files:**
- Create: `app/healing/patcher.py`
- Test: `tests/test_repair_patcher.py`

**Interfaces:**
- Consumes: `ExtractionSchema`, `RepairPlan`, `RepairType`
- Produces: `RepairPatcher.apply_patch(schema: ExtractionSchema, plan: RepairPlan) -> ExtractionSchema`

- [ ] **Step 1: Write the failing patcher test**
Create `tests/test_repair_patcher.py` verifying selective patching of CSS selectors, XPath expressions, regex patterns, table modes, semantic filtering parameters, chunking configs, and extraction strategies without modifying unaffected fields.

- [ ] **Step 2: Run test to verify it fails**
Run: `python -m pytest tests/test_repair_patcher.py -v`
Expected: FAIL (ModuleNotFoundError)

- [ ] **Step 3: Write minimal implementation**
Create `app/healing/patcher.py` with pure functions to patch `ExtractionSchema` non-destructively.

- [ ] **Step 4: Run test to verify it passes**
Run: `python -m pytest tests/test_repair_patcher.py -v`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add app/healing/patcher.py tests/test_repair_patcher.py
git commit -m "feat(healing): add minimal-patch repair patcher"
```

---

### Task 3: Deterministic Repair Evaluator & Regression Protection

**Files:**
- Create: `app/healing/evaluator.py`
- Test: `tests/test_repair_evaluator.py`

**Interfaces:**
- Consumes: `ValidationResult` (before), `ValidationResult` (after), `DiagnosisResult`, `RepairPlan`
- Produces: `RepairEvaluator.evaluate(before: ValidationResult, after: ValidationResult, diagnosis: DiagnosisResult, plan: RepairPlan) -> RepairEvaluation`

- [ ] **Step 1: Write the failing evaluator test**
Create `tests/test_repair_evaluator.py` testing:
- Healthy transition condition (`after.health_score >= 0.80` + critical failure resolved).
- Delta improvement condition (`after.health_score >= before.health_score + 0.10`).
- Regression rejection (healthy field dropping $>5\%$ coverage).
- Duplicate explosion rejection ($>30\%$).

- [ ] **Step 2: Run test to verify it fails**
Run: `python -m pytest tests/test_repair_evaluator.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**
Create `app/healing/evaluator.py` implementing `RepairEvaluator` with snapshot comparisons and strict regression checks.

- [ ] **Step 4: Run test to verify it passes**
Run: `python -m pytest tests/test_repair_evaluator.py -v`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add app/healing/evaluator.py tests/test_repair_evaluator.py
git commit -m "feat(healing): add deterministic repair evaluator and regression guards"
```

---

### Task 4: Fresh Page Evidence Collector

**Files:**
- Create: `app/healing/evidence_collector.py`
- Test: `tests/test_repair_evidence.py`

**Interfaces:**
- Consumes: `ScrapingTask`, `ScraperAgent`, `ExtractionEngine`, `ValidationEngine`
- Produces: `RepairEvidenceCollector.collect_evidence(task: ScrapingTask, current_schema: ExtractionSchema) -> tuple[list[RawPage], bool]`

- [ ] **Step 1: Write the failing evidence collector test**
Create `tests/test_repair_evidence.py` testing fresh DOM acquisition via provider, transient recovery detection (`NO_REPAIR_REQUIRED`), and HTML structure summarization.

- [ ] **Step 2: Run test to verify it fails**
Run: `python -m pytest tests/test_repair_evidence.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**
Create `app/healing/evidence_collector.py` to fetch fresh page snapshots and evaluate if current configuration unexpectedly passes.

- [ ] **Step 4: Run test to verify it passes**
Run: `python -m pytest tests/test_repair_evidence.py -v`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add app/healing/evidence_collector.py tests/test_repair_evidence.py
git commit -m "feat(healing): add fresh page repair evidence collector"
```

---

### Task 5: Repair Memory & Domain Signatures

**Files:**
- Create: `app/healing/memory.py`
- Test: `tests/test_repair_memory.py`

**Interfaces:**
- Consumes: Domain, URL, HTML structure, `RepairPlan`, `RepairEvaluation`
- Produces: `RepairMemory.generate_signature(url: str, html: str, fields: list[str]) -> str`, `RepairMemory.record_success(...)`, `RepairMemory.find_similar_repairs(...)`

- [ ] **Step 1: Write the failing memory test**
Create `tests/test_repair_memory.py` verifying signature generation, recording successful repairs, and retrieving matching repair templates for similar DOM signatures.

- [ ] **Step 2: Run test to verify it fails**
Run: `python -m pytest tests/test_repair_memory.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**
Create `app/healing/memory.py` providing in-memory / structured file storage for proven repair patterns.

- [ ] **Step 4: Run test to verify it passes**
Run: `python -m pytest tests/test_repair_memory.py -v`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add app/healing/memory.py tests/test_repair_memory.py
git commit -m "feat(healing): add domain signature generation and repair memory"
```

---

### Task 6: Healing Planner & Adaptive Candidate Ranking

**Files:**
- Create: `app/healing/planner.py`
- Test: `tests/test_healing_planner.py`

**Interfaces:**
- Consumes: `ScrapingTask`, `DiagnosisResult`, `ValidationResult`, `list[RawPage]`, `ExtractionSchema`, `RepairMemory`
- Produces: `HealingPlanner.generate_candidates(...) -> list[RepairCandidate]`

- [ ] **Step 1: Write the failing planner test**
Create `tests/test_healing_planner.py` testing candidate generation from fresh DOM evidence, strict non-invention constraints, Crawl4AI-inspired candidate scoring formula, and ranking.

- [ ] **Step 2: Run test to verify it fails**
Run: `python -m pytest tests/test_healing_planner.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**
Create `app/healing/planner.py` with Qwen3:8b prompt generation, structured JSON repair parsing, and candidate scoring.

- [ ] **Step 4: Run test to verify it passes**
Run: `python -m pytest tests/test_healing_planner.py -v`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add app/healing/planner.py tests/test_healing_planner.py
git commit -m "feat(healing): add healing planner with adaptive candidate ranking"
```

---

### Task 7: Repair Executor

**Files:**
- Create: `app/healing/executor.py`
- Test: `tests/test_repair_executor.py`

**Interfaces:**
- Consumes: `RepairPlan`, `ExtractionSchema`, `ScraperAgent`
- Produces: `RepairExecutor.apply_candidate(plan: RepairPlan, schema: ExtractionSchema) -> ExtractionSchema`

- [ ] **Step 1: Write the failing executor test**
Create `tests/test_repair_executor.py` testing Level 1 extraction schema candidate execution, Level 2 scraper execution parameters, and Level 3 fallback handling.

- [ ] **Step 2: Run test to verify it fails**
Run: `python -m pytest tests/test_repair_executor.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**
Create `app/healing/executor.py` applying candidate configs safely without arbitrary code execution.

- [ ] **Step 4: Run test to verify it passes**
Run: `python -m pytest tests/test_repair_executor.py -v`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add app/healing/executor.py tests/test_repair_executor.py
git commit -m "feat(healing): add safe repair executor"
```

---

### Task 8: Healing Engine & Canary Loop

**Files:**
- Create: `app/healing/engine.py`
- Test: `tests/test_healing_engine.py`

**Interfaces:**
- Consumes: `ScrapingTask`, `DiagnosisResult`, `ValidationResult`, `ExtractionSchema`, `ScraperAgent`, `ExtractionEngine`, `ValidationEngine`
- Produces: `HealingEngine.attempt_repair(...) -> tuple[bool, Optional[ExtractionSchema], RepairEvaluation, list[dict]]`

- [ ] **Step 1: Write the failing healing engine test**
Create `tests/test_healing_engine.py` executing a full canary cycle (fresh evidence $\rightarrow$ candidate plan $\rightarrow$ canary extract $\rightarrow$ validation $\rightarrow$ evaluate $\rightarrow$ accept/reject).

- [ ] **Step 2: Run test to verify it fails**
Run: `python -m pytest tests/test_healing_engine.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**
Create `app/healing/engine.py` orchestrating candidate lifecycle, bounded retries, and memory updates.

- [ ] **Step 4: Run test to verify it passes**
Run: `python -m pytest tests/test_healing_engine.py -v`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add app/healing/engine.py tests/test_healing_engine.py
git commit -m "feat(healing): add healing engine orchestrator"
```

---

### Task 9: Healing Agent & LangGraph Workflow Feedback Loop

**Files:**
- Modify: `app/agents/healing.py`
- Modify: `app/graph/state.py`
- Modify: `app/graph/workflow.py`
- Test: `tests/test_healing_workflow.py`

**Interfaces:**
- Updates `ScrapingGraphState` with `repair_attempt`, `repair_history`, `repair_plan`, `candidate_configuration`, `repair_evaluation`.
- Updates `create_scraping_workflow()` with `should_repair`, `should_heal`, `healing_node`, `repair_apply_node`, `escalate_node`.

- [ ] **Step 1: Write the failing workflow test**
Create `tests/test_healing_workflow.py` testing:
- Healthy bypass to END.
- Unjustified failure (`SOURCE_DATA_QUALITY`) bypass to END.
- Low-confidence diagnosis routing directly to ESCALATE $\rightarrow$ END.
- Actionable degradation routing to diagnosis $\rightarrow$ healing $\rightarrow$ repair_apply $\rightarrow$ scraper $\rightarrow$ extraction $\rightarrow$ validation.
- Successful repair ending with `self_healed=True`.
- Exhausted retries (`MAX_REPAIR_ATTEMPTS=3`) ending with `escalated=True`.

- [ ] **Step 2: Run test to verify it fails**
Run: `python -m pytest tests/test_healing_workflow.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**
Update `app/agents/healing.py`, `app/graph/state.py`, and `app/graph/workflow.py`.

- [ ] **Step 4: Run test to verify it passes**
Run: `python -m pytest tests/test_healing_workflow.py -v`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add app/agents/healing.py app/graph/state.py app/graph/workflow.py tests/test_healing_workflow.py
git commit -m "feat(workflow): integrate self-healing feedback loop and escalation routing into LangGraph"
```

---

### Task 10: FastAPI API Integration & Metadata

**Files:**
- Modify: `app/main.py`
- Test: `tests/test_healing_api.py`

**Interfaces:**
- `/scrape` returns updated `metadata`: `self_healed`, `repair_attempts`, `health_before`, `health_after`, `repair_type`, `repair_history`, `scraper_provider`.

- [ ] **Step 1: Write the failing API test**
Create `tests/test_healing_api.py` validating that `/scrape` properly formats self-healed metadata vs escalated metadata.

- [ ] **Step 2: Run test to verify it fails**
Run: `python -m pytest tests/test_healing_api.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**
Update `app/main.py` to populate self-healing metadata on response.

- [ ] **Step 4: Run test to verify it passes**
Run: `python -m pytest tests/test_healing_api.py -v`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add app/main.py tests/test_healing_api.py
git commit -m "feat(api): expose self-healing metadata and repair metrics on /scrape"
```

---

### Task 11: End-to-End Controlled Self-Healing Verification Suite

**Files:**
- Create: `tests/test_healing_e2e_scenarios.py`
- Test: `tests/test_healing_e2e_scenarios.py`

- [ ] **Step 1: Write and run end-to-end controlled scenarios**
Test Case 1: CSS selector drift (Old `.product-card .title` $\rightarrow$ New `.product-item .product-name`).
Test Case 2: Strategy switch (Broken CSS $\rightarrow$ Semantic + LLM).
Test Case 3: Regex drift (Phone/Date format shift).
Test Case 4: Table structure change.
Test Case 5: Source quality issue (Bypass repair $\rightarrow$ END).
Test Case 6: Repeated failures $\rightarrow$ Max retries $\rightarrow$ ESCALATE.

- [ ] **Step 2: Run test to verify it passes**
Run: `python -m pytest tests/test_healing_e2e_scenarios.py -v`
Expected: PASS

- [ ] **Step 3: Commit**
```bash
git add tests/test_healing_e2e_scenarios.py
git commit -m "test(healing): add controlled end-to-end self-healing evaluation scenarios"
```

---

### Task 12: Documentation & Complete Test Suite Run

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update README.md**
Document Phase 5 self-healing architecture, repair lifecycle, Crawl4AI-inspired adaptive concepts, canary testing, acceptance rules, memory system, provider behavior, and metrics.

- [ ] **Step 2: Run full test suite**
Run: `python -m pytest tests -v`
Expected: All tests pass (Phase 1–4 + Phase 5).

- [ ] **Step 3: Commit**
```bash
git add README.md
git commit -m "docs: document Phase 5 autonomous self-healing architecture and metrics in README"
```
