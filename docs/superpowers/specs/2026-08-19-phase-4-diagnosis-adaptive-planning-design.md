# Phase 4: Failure Diagnosis & Adaptive Repair Planning Design Specification

## 1. Overview & Goal
Phase 4 introduces the **Failure Diagnosis Subsystem** and **Adaptive Repair Planning** to the **Scrape_the_Verse** multi-agent pipeline.
When scraping or extraction degrades or fails, the Diagnosis Agent determines:
- **WHAT** failed (Failure Category & Affected Stage)
- **WHERE** it failed (Affected Fields, Selectors, DOM locations)
- **WHY** it likely failed (Root Cause & Confidence)
- **WHAT** should be repaired (Repair Strategy & Repair Targets)

Phase 4 is strictly **diagnostic and advisory**. It produces a structured `DiagnosisResult` with a concrete `repair_strategy`, but **DOES NOT** execute code modification, selector rewriting, or autonomous retries (reserved for Phase 5).

---

## 2. Architecture & Pipeline

```
Validation Result (status in ["broken", "unstable", "degraded"] with failures)
                               │
                               ▼
               ┌───────────────────────────────┐
               │   DiagnosisEvidenceBuilder    │ ── Reuses ContentChunker & SemanticFilter
               └───────────────┬───────────────┘
                               │
                               ▼
               ┌───────────────────────────────┐
               │        DiagnosisEngine        │
               └───────────────┬───────────────┘
                               │
         ┌─────────────────────┴─────────────────────┐
         ▼                                           ▼
┌──────────────────┐                       ┌──────────────────┐
│  Deterministic   │                       │  LLM Diagnostic  │
│ Rule Classifier  │                       │   (Qwen3:8b)     │
└────────┬─────────┘                       └────────┬─────────┘
         │ (Obvious failures)                       │ (Ambiguous/DOM drift)
         └─────────────────────┬────────────────────┘
                               │
                               ▼
                        DiagnosisResult
```

---

## 3. LangGraph Workflow with Conditional Routing

```
START ──► [planner] ──► [scraper] ──► [extraction] ──► [validation]
                                                             │
                                       ┌─────────────────────┴─────────────────────┐
                                       │ Needs Diagnosis?                          │
                                       │ (broken / unstable / critical failures)   │
                                       └──────────┬───────────────────────┬────────┘
                                                  │ NO                    │ YES
                                                  ▼                       ▼
                                                 END              [diagnosis_node]
                                                                          │
                                                                          ▼
                                                                         END
```

---

## 4. Root Cause & Repair Strategy Taxonomy

### Root Causes (`RootCause`):
- `SELECTOR_DRIFT`: DOM element names, classes, or hierarchy changed.
- `DOM_STRUCTURE_CHANGE`: Container structure drastically altered (e.g. div to table or custom web components).
- `SCRAPER_OUTPUT_MISSING`: Scraper returned empty content or got blocked.
- `EXTRACTION_DEGRADATION`: Raw page content present, but zero records extracted.
- `SCHEMA_MISMATCH`: Required fields missing from extraction schema or output.
- `PAGINATION_FAILURE`: Yield dropped significantly below expectation.
- `RENDERING_FAILURE`: Incomplete JS rendering / missing client-side content.
- `REGEX_PATTERN_FAILURE`: Regex pattern no longer matches textual representation.
- `TABLE_STRUCTURE_CHANGE`: HTML table layout changed (e.g. divs replacing tables).
- `LLM_EXTRACTION_FAILURE`: LLM output was malformed or failed schema requirements.
- `SOURCE_DATA_QUALITY`: Scraper and extraction are functioning, but source data inherently lacks the requested information.
- `UNKNOWN`: Insufficient evidence to pinpoint root cause.

### Repair Strategies (`RepairStrategy`):
- `RETRY_SAME_CONFIGURATION`
- `REPAIR_CSS_SELECTORS`
- `REPAIR_XPATH_SELECTORS`
- `REPAIR_REGEX_PATTERN`
- `REPAIR_TABLE_SCHEMA`
- `REPAIR_EXTRACTION_SCHEMA`
- `SWITCH_EXTRACTION_STRATEGY`
- `REGENERATE_LLM_EXTRACTION_SCHEMA`
- `ADJUST_CONTENT_CHUNKING`
- `ADJUST_SEMANTIC_FILTERING`
- `RECHECK_RAW_CONTENT`
- `ESCALATE`

---

## 5. Fallback Scraper Provider Logic
To support local development, unit testing, and environments without active Bright Data API credentials:
```
SCRAPER_PROVIDER == "brightdata"
       │
       ▼
Bright Data API Key Configured?
       ├── YES ──► BrightDataClient (Scraper Studio)
       └── NO  ──► Native HTTP Scraper (httpx transport)
```
