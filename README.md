# Self-Healing Multi-Agent Web Scraping System

A plain-language, multi-agent, autonomous self-healing web scraping framework powered by **LangGraph**, **Ollama**, local **Qwen3:8b**, **Bright Data Scraper Studio**, a modular **Extraction Engine**, a deterministic **Validation Engine**, a **Failure Diagnosis Subsystem**, and an **Autonomous Self-Healing Feedback Loop (Phase 5)**.

---

## 1. Project Purpose & Overview

Traditional web scraping pipelines frequently break due to dynamic DOM redesigns, anti-bot protections, pagination alterations, and selector drift. **Scrape_the_Verse** implements an autonomous, self-healing scraping system:
1. Users submit web scraping objectives in **plain, natural language** along with target URLs (either supplied in structured lists or embedded in the text query).
2. A **Scraping Planner Agent** translates the human objective into a deterministic scraping task specification.
3. Sub-agents coordinate across the lifecycle: dispatching crawl jobs to **Bright Data** (or native HTTP fallback), extracting structured records via our modular extraction engine, validating quality against schemas, diagnosing runtime failures, and executing autonomous self-healing repairs.
4. If a failure occurs, the system re-acquires fresh DOM evidence, generates minimal evidence-grounded repair plans, runs canary test runs, and enforces deterministic validation gates before accepting repairs.

> [!IMPORTANT]
> **No URL Discovery / Search Engine Agent**: The system operates exclusively on URLs provided explicitly by the user or identified in the user's natural language request. The system never invents URLs or uses external search engines.

---

## 2. Autonomous Self-Healing Architecture (Phase 5)

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
├── schemas.py              # Strict Pydantic models (RepairPlan, RepairCandidate, RepairEvaluation, RepairMemoryRecord)
├── evidence_collector.py   # RepairEvidenceCollector (fetches fresh DOM snapshots & detects transient recovery)
├── planner.py              # HealingPlanner (Qwen3:8b prompt construction & Crawl4AI-inspired candidate ranking)
├── patcher.py              # RepairPatcher (pure functions applying minimal schema patches)
├── executor.py             # RepairExecutor (safe execution without arbitrary code injection)
├── evaluator.py            # RepairEvaluator (deterministic validation gate with regression protection)
├── memory.py               # RepairMemory (domain/DOM structural signature store for pattern reuse)
└── engine.py               # HealingEngine (end-to-end self-healing coordinator)
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

## 5. Crawl4AI-Inspired Adaptive Signals & Candidate Scoring

Crawl4AI concepts are used as architectural inspiration for adaptive content selection and candidate scoring:
1. **Coverage**: Ratio of required fields successfully extracted with valid non-null values.
2. **Consistency**: Penalizes candidate extractions that introduce noisy, non-uniform, or boilerplate records.
3. **Saturation / Diminishing Returns**: Halts exploration when successive attempts yield $< 2\%$ information gain.
4. **Semantic / Cosine Filtering**: Uses `ContentChunker` + `SemanticFilter` to locate relevant content blocks when structural DOM selectors break.
5. **Candidate Scoring Function**:
   $$\text{Score} = 0.35 \times \text{confidence} + 0.30 \times \text{expected\_improvement} + 0.20 \times \text{strategy\_reliability} + 0.10 \times \text{historical\_success} - 0.05 \times \text{risk}$$

> [!NOTE]
> Our system does **not** install or require Crawl4AI as a runtime dependency.

---

## 6. Deterministic Acceptance Rules & Regression Protection

The LLM **never** approves its own repairs. The deterministic `RepairEvaluator` holds the gate.
A repair candidate is accepted if and only if:
1. **No Severe Regression**: No previously healthy field ($\ge 80\%$ coverage) drops by more than $5\%$ coverage.
2. **Quality Sanity**: Duplicate rate does not explode ($< 30\%$) and schema validity does not degrade.
3. **Improvement Condition** (either of the following):
   - **Condition A (Healthy Transition)**: Candidate achieves `health_score >= 0.80` AND critical failures identified by Diagnosis are resolved.
   - **Condition B (Substantial Delta)**: Candidate `health_score >= before.health + MIN_HEALTH_IMPROVEMENT` (default $0.10$).

---

## 7. Scraper Provider Behavior

The system respects `SCRAPER_PROVIDER` settings:
- **`auto`**: Uses Bright Data if valid credentials exist; otherwise falls back to local HTTP scraper.
- **`brightdata`**: Requires Bright Data credentials; errors if unconfigured.
- **`local`**: Uses native HTTP scraper.

Every execution records `scraper_provider` inside the result metadata.

---

## 8. API Reference

### `POST /scrape` (Execute Full Pipeline)

**Request:**
```json
{
  "query": "Scrape product title and price from the provided store",
  "target_urls": [
    "https://store.example.com/products"
  ],
  "max_records": 20
}
```

**Self-Healed Success Response:**
```json
{
  "task_id": "8f0be24c-b4db-4b68-80f4-5f54316d6342",
  "status": "success",
  "records": [
    {
      "title": "MacBook Pro 16",
      "price": "$2499"
    }
  ],
  "metadata": {
    "task_id": "8f0be24c-b4db-4b68-80f4-5f54316d6342",
    "record_count": 1,
    "health_score": 0.95,
    "quality_score": 0.92,
    "scraper_provider": "local",
    "self_healed": true,
    "repair_attempts": 1,
    "health_before": 0.32,
    "health_after": 0.95,
    "repair_type": "REPAIR_CSS_SELECTORS",
    "repair_history": [
      {
        "attempt": 1,
        "repair_type": "REPAIR_CSS_SELECTORS",
        "confidence": 0.95,
        "health_before": 0.32,
        "health_after": 0.95,
        "accepted": true
      }
    ]
  },
  "error": null
}
```

**Escalated Response (Retries Exhausted):**
```json
{
  "task_id": "9a1bc24d-e5fb-4c78-90f5-6g64316d7453",
  "status": "failed",
  "records": [],
  "metadata": {
    "task_id": "9a1bc24d-e5fb-4c78-90f5-6g64316d7453",
    "record_count": 0,
    "self_healed": false,
    "escalated": true,
    "repair_attempts": 3,
    "health_before": 0.20,
    "health_after": 0.35
  },
  "error": "Unable to recover scraper after bounded repair attempts"
}
```

---

## 9. Running Tests

Run full test suite:
```powershell
python -m pytest tests -v
```

Run Phase 5 self-healing tests specifically:
```powershell
python -m pytest tests/test_healing*.py tests/test_repair*.py -v
```
