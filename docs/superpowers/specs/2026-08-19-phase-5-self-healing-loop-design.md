# Phase 5: Autonomous Self-Healing Pipeline Design Specification

## 1. Executive Summary & Objective
Phase 5 introduces the core intelligence of **Scrape_the_Verse**: **Autonomous Self-Healing of Scraping and Extraction Failures**.
When scraping or extraction degrades or fails in production, the system must:
1. Detect the failure deterministically through the Phase 3 Validation Engine.
2. Determine whether repair is justified (filtering out inherent source data quality issues).
3. Diagnose the failure mechanism and root cause via the Phase 4 Diagnosis Subsystem.
4. Collect fresh raw page evidence (`RepairEvidenceCollector`) to observe DOM/layout shifts.
5. Synthesize candidate minimal repair plans grounded strictly in evidence using local Qwen3:8b.
6. Apply candidate repairs to extraction schemas or scraper configurations without executing arbitrary untrusted code.
7. Perform canary executions (re-scrape/re-extract) and re-validate deterministically.
8. Evaluate candidate performance against previous baselines with strict regression guards.
9. Accept improved repairs, retry alternative ranked candidates within bounded limits, or safely escalate to human operators.

**Hard Invariant**: The LLM *never* approves its own repair. The deterministic `RepairEvaluator` holds the gate.

---

## 2. Architecture & End-to-End Self-Healing Workflow

```
                         VALIDATION
                             │
                   repair justified?
                     /            \
                   NO              YES
                   │                │
                   ▼                ▼
                  END          DIAGNOSIS
                                  │
                          diagnosis confident?
                           /              \
                         NO                YES
                         │                  │
                         ▼                  ▼
                      ESCALATE     Fresh Page Evidence
                                   (RepairEvidenceCollector)
                                           │
                                           ▼
                                    Healing Planner
                                  (Generates Candidates)
                                           │
                                           ▼
                                    Rank Candidates
                                           │
                                           ▼
                                    Repair Executor
                                           │
                                           ▼
                                      Canary Run
                                           │
                                      Extraction
                                           │
                                      Validation
                                           │
                                    Repair Evaluator
                                       /         \
                                    ACCEPT       REJECT
                                      │             │
                                      ▼             ▼
                                     END       next candidate
                                                   │
                                              retry limit?
                                               /       \
                                             NO         YES
                                             │           │
                                             └─ loop    ESCALATE
```

---

## 3. Subsystem Organization (`app/healing/`)

```
app/healing/
├── __init__.py
├── schemas.py              # RepairPlan, RepairCandidate, RepairEvaluation, RepairMemoryRecord, RepairType
├── evidence_collector.py   # RepairEvidenceCollector (fetches fresh HTML/DOM snapshot via configured provider)
├── planner.py              # HealingPlanner (generates candidates, Crawl4AI-inspired scoring)
├── patcher.py              # RepairPatcher (pure functions for patching ExtractionSchema)
├── executor.py             # RepairExecutor (applies candidate schema/config)
├── evaluator.py            # RepairEvaluator (canary evaluation, regression guards, before/after metrics)
├── memory.py               # RepairMemory (signature store for cross-run repair pattern reuse)
└── engine.py               # HealingEngine (orchestrates the end-to-end healing loop)
```

---

## 4. Multi-Level Repair Hierarchy (Minimal-Patch Principle)

The healing engine strictly prioritizes low-risk, deterministic extraction repairs before touching scraper-level configurations:

```
LEVEL 1: Extraction-Level Repair (Highest Priority, Lowest Risk)
├── REPAIR_CSS_SELECTORS          (Update drifted CSS selectors or container base selector)
├── REPAIR_XPATH_SELECTORS        (Update drifted XPath expressions)
├── REPAIR_REGEX_PATTERN          (Adjust parsing regex patterns)
├── REPAIR_TABLE_SCHEMA           (Switch table parsing mode / header extraction)
├── REPAIR_SEMANTIC_FILTER        (Adjust similarity threshold / top-k chunking)
├── REPAIR_CHUNKING               (Adjust chunk size / overlap window)
├── REPAIR_LLM_EXTRACTION_SCHEMA  (Regenerate LLM extraction schema / prompts)
└── SWITCH_EXTRACTION_STRATEGY    (e.g., CSS -> Table -> Semantic+LLM)

       ↓ (if extraction repairs fail or root cause is scraper-level)

LEVEL 2: Scraper Configuration Repair
└── REPAIR_SCRAPER_CONFIG         (Target execution settings, headers, pagination params)

       ↓ (if local scraper repairs fail and collector-level issue identified)

LEVEL 3: Bright Data Self-Healing / Refactor Fallback
└── BRIGHTDATA_REFACTOR_FALLBACK  (Optional collector refactor API for Bright Data scraper studio)

       ↓ (if exhausted or unrecoverable)

ESCALATE                          (Structured handoff with diagnosis, attempts, and evidence)
```

---

## 5. Structured Schemas

### A. Repair Types & Status Enums
```python
class RepairType(str, Enum):
    NO_REPAIR_REQUIRED = "NO_REPAIR_REQUIRED"
    REPAIR_CSS_SELECTORS = "REPAIR_CSS_SELECTORS"
    REPAIR_XPATH_SELECTORS = "REPAIR_XPATH_SELECTORS"
    REPAIR_REGEX_PATTERN = "REPAIR_REGEX_PATTERN"
    REPAIR_TABLE_SCHEMA = "REPAIR_TABLE_SCHEMA"
    REPAIR_EXTRACTION_SCHEMA = "REPAIR_EXTRACTION_SCHEMA"
    SWITCH_EXTRACTION_STRATEGY = "SWITCH_EXTRACTION_STRATEGY"
    REPAIR_SEMANTIC_FILTER = "REPAIR_SEMANTIC_FILTER"
    REPAIR_CHUNKING = "REPAIR_CHUNKING"
    REPAIR_LLM_EXTRACTION_SCHEMA = "REPAIR_LLM_EXTRACTION_SCHEMA"
    REPAIR_CONTENT_TARGET = "REPAIR_CONTENT_TARGET"
    REPAIR_SCRAPER_CONFIG = "REPAIR_SCRAPER_CONFIG"
    BRIGHTDATA_REFACTOR_FALLBACK = "BRIGHTDATA_REFACTOR_FALLBACK"
    RETRY_WITH_ALTERNATIVE_STRATEGY = "RETRY_WITH_ALTERNATIVE_STRATEGY"
    ESCALATE = "ESCALATE"

class RepairStatus(str, Enum):
    PROPOSED = "proposed"
    APPLIED = "applied"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    ESCALATED = "escalated"
```

### B. RepairPlan Schema
```python
class RepairPlan(BaseModel):
    repair_id: str = Field(default_factory=lambda: str(uuid4()))
    repair_type: RepairType
    target_component: Literal["extraction", "scraper", "collector"] = "extraction"
    affected_fields: list[str] = Field(default_factory=list)
    previous_configuration: dict[str, Any] = Field(default_factory=dict)
    proposed_configuration: dict[str, Any] = Field(default_factory=dict)
    patch: dict[str, Any] = Field(default_factory=dict)
    reason: str
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    expected_improvement: dict[str, float] = Field(default_factory=dict)
    test_requirements: list[str] = Field(default_factory=list)
    risk_level: Literal["low", "medium", "high"] = "low"
    level: int = Field(default=1, ge=1, le=3)
```

### C. RepairEvaluation & Snapshot Schema
```python
class PerformanceSnapshot(BaseModel):
    health: float
    quality: float
    records: int
    field_coverage: dict[str, float] = Field(default_factory=dict)
    duplicate_rate: float = 0.0
    schema_valid_rate: float = 1.0
    strategy_used: str = "unknown"

class RepairEvaluation(BaseModel):
    repair_id: str
    before: PerformanceSnapshot
    after: PerformanceSnapshot
    improvement: float
    critical_failure_resolved: bool
    regression_detected: bool
    accepted: bool
    rejection_reason: Optional[str] = None
```

---

## 6. Fresh Page Acquisition (`RepairEvidenceCollector`)

When a layout changes, the broken extraction result alone does not contain the new selectors.
`RepairEvidenceCollector`:
1. Inspects the target URL(s) and scraping task.
2. Invokes the active scraper provider (`brightdata` or `local` HTTP scraper) to fetch a fresh HTML/text snapshot.
3. Chunks and extracts structural evidence (e.g. tag distributions, class signatures, repeating article/card containers).
4. Re-runs a quick check: if the fresh scrape produces healthy results with existing configuration (transient glitch), returns `NO_REPAIR_REQUIRED`.
5. Otherwise, packages the fresh DOM snapshot as grounded context for `HealingPlanner`.

---

## 7. Crawl4AI-Inspired Adaptive Signals & Candidate Generation

1. **Coverage**: $\text{coverage} = \frac{\text{valid non-null requested fields}}{\text{total requested fields}}$.
2. **Consistency**: Penalizes records that vary wildly in schema/structure across a single extraction batch.
3. **Saturation / Diminishing Returns**: Stops candidate testing if successive attempts yield $< 2\%$ information gain.
4. **Semantic / Cosine Recovery**: When CSS/XPath selectors fail, uses `ContentChunker` + `SemanticFilter` to isolate product/entity chunks and feed them to Qwen3:8b for schema extraction.
5. **Candidate Scoring Function**:
   $$\text{Score} = 0.35 \times \text{confidence} + 0.30 \times \text{expected\_improvement} + 0.20 \times \text{strategy\_reliability} + 0.10 \times \text{historical\_success} - 0.05 \times \text{risk}$$

---

## 8. Deterministic Acceptance Rules & Regression Protection

A candidate repair is **accepted** by `RepairEvaluator` if and only if:
1. **No Severe Regression**: No previously healthy field ($\ge 80\%$ coverage) drops by more than $5\%$ coverage.
2. **Quality Retention**: Duplicate rate does not explode ($< 30\%$) and schema validity does not worsen.
3. **Improvement Condition** (either of the following):
   - **Condition A (Healthy Transition)**: Candidate achieves `health_score >= 0.80` AND critical failures identified by Diagnosis are resolved.
   - **Condition B (Substantial Delta)**: Candidate `health_score >= before.health + MIN_HEALTH_IMPROVEMENT` (default $0.10$).

---

## 9. Repair Memory & Domain Signatures

- Generates a domain structure signature: $\text{hash}(\text{domain} + \text{URL path pattern} + \text{DOM tag signature} + \text{field names})$.
- Records successful repair events in a structured format:
  ```json
  {
    "domain": "example.com",
    "signature": "a1b2c3d4",
    "root_cause": "SELECTOR_DRIFT",
    "repair_type": "REPAIR_CSS_SELECTORS",
    "successful_patch": {"product_name": ".product-item h2"},
    "health_before": 0.31,
    "health_after": 0.94,
    "timestamp": "2026-08-19T13:45:00"
  }
  ```
- Before prompting LLM, queries memory for identical/similar signatures to seed candidate generation with historically successful patterns.

---

## 10. LangGraph Feedback Loop Integration

```python
class ScrapingGraphState(TypedDict, total=False):
    task_id: str
    original_user_query: str
    scraping_task: Optional[ScrapingTask]
    target_urls: list[str]
    scraper_provider: str
    scraper_id: Optional[str]
    scraper_version: Optional[str]
    scraper_code: Optional[str]
    raw_results: Optional[list[dict[str, Any]]]
    extracted_results: Optional[list[dict[str, Any]]]
    validation_result: Optional[dict[str, Any]]
    diagnosis_result: Optional[dict[str, Any]]
    repair_plan: Optional[dict[str, Any]]
    candidate_configuration: Optional[dict[str, Any]]
    candidate_scraper_version: Optional[str]
    repair_evaluation: Optional[dict[str, Any]]
    repair_history: list[dict[str, Any]]
    repair_attempt: int
    failure: Optional[Any]
    final_output: Optional[ScrapingResult]
```

### Conditional Edges:
- `validation -> should_repair(state)`:
  - If status == `"healthy"` $\rightarrow$ `END`.
  - If root_cause == `"SOURCE_DATA_QUALITY"` (inherent content issue, repair not justified) $\rightarrow$ `END`.
  - If attempts $\ge$ `MAX_REPAIR_ATTEMPTS` $\rightarrow$ `diagnosis` (routes to escalate) $\rightarrow$ `END`.
  - If actionable degradation $\rightarrow$ `diagnosis`.
- `diagnosis -> should_heal(state)`:
  - If confidence $< 0.50$ or root_cause == `UNKNOWN` $\rightarrow$ `healing` (produces `ESCALATE`) $\rightarrow$ `END`.
  - If confident actionable diagnosis $\rightarrow$ `healing`.
- `healing -> repair_apply`: Applies candidate `ExtractionSchema`.
- `repair_apply -> scraper`: Triggers canary scrape/extract/validate loop.

---

## 11. API Metadata Contract

`/scrape` response includes:
```json
{
  "task_id": "...",
  "status": "success",
  "records": [...],
  "metadata": {
    "scraper_provider": "local",
    "self_healed": true,
    "repair_attempts": 1,
    "repair_type": "REPAIR_CSS_SELECTORS",
    "health_before": 0.31,
    "health_after": 0.94,
    "repair_history": [...]
  },
  "error": null
}
```

---

## 12. Verification & Testing Suite

Comprehensive test coverage across:
1. `tests/test_healing_schema.py`: Pydantic validations, Enums, snapshots.
2. `tests/test_repair_evidence.py`: `RepairEvidenceCollector` fetching fresh DOM and detecting `NO_REPAIR_REQUIRED`.
3. `tests/test_healing_planner.py`: Candidate generation, Crawl4AI-inspired scoring.
4. `tests/test_repair_patcher.py`: Minimal schema patching for CSS, XPath, Regex, Table, Semantic, LLM.
5. `tests/test_repair_executor.py`: Safe candidate execution without arbitrary code injection.
6. `tests/test_repair_evaluator.py`: Acceptance conditions (health threshold + delta), regression guard.
7. `tests/test_repair_memory.py`: Signature hashing, pattern persistence, candidate reuse.
8. `tests/test_healing_engine.py`: Controlled lifecycle (broken selector $\rightarrow$ fresh evidence $\rightarrow$ candidate $\rightarrow$ canary $\rightarrow$ accept).
9. `tests/test_healing_workflow.py`: LangGraph feedback loop, bounded retry, escalation.
10. `tests/test_healing_api.py`: FastAPI `/scrape` response metadata.
