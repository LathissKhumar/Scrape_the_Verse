# Self-Healing Multi-Agent Web Scraping System

A plain-language, multi-agent, self-healing web scraping framework powered by **LangGraph**, **Ollama**, local **Qwen3:8b**, **Bright Data Scraper Studio**, a modular **Extraction Engine**, a deterministic **Validation Engine**, and an intelligent **Failure Diagnosis Subsystem**.

---

## 1. Project Purpose & Overview

Traditional web scraping pipelines frequently break due to dynamic DOM structures, anti-bot protections, pagination changes, and selector drift. This project implements an autonomous, self-healing scraping system where:
1. Users submit web scraping objectives in **plain, natural language** along with target URLs (either supplied in structured lists or referenced within the prompt).
2. A **Scraping Planner Agent** interprets the human objective into a deterministic scraping task specification.
3. Sub-agents coordinate across the lifecycle: dispatching crawl jobs to **Bright Data** (or native HTTP fallback), extracting structured records via our modular extraction engine, validating quality against schemas, diagnosing runtime failures, and planning adaptive repairs.

> [!IMPORTANT]
> **No URL Discovery / Search Engine Agent**: The system operates exclusively on URLs provided explicitly by the user or identified in the user's natural language request. The system never invents URLs or uses external search engines.

---

## 2. Multi-Agent Architecture & Lifecycle

```
Plain-Language User Request + URLs
                 │
                 ▼
      ┌──────────────────────┐
      │ Scraping Planner     │ ── Translates natural language into ScrapingTask
      └──────────┬───────────┘
                 │
                 ▼
      ┌──────────────────────┐
      │    Scraper Agent     │ ── Dispatches crawl jobs to Bright Data (or native fallback)
      └──────────┬───────────┘
                 │
                 ▼
      ┌──────────────────────┐
      │   Extraction Agent   │ ── Modular Extraction Engine (CSS/XPath/Regex/Table/LLM)
      └──────────┬───────────┘
                 │
                 ▼
      ┌──────────────────────┐
      │   Validation Agent   │ ── Deterministic Validation & Health Scoring
      └──────────┬───────────┘
                 │
           ┌─────┴─────┐
           │ Healthy?  │
           └──┬─────┬──┘
          YES │     │ NO (degraded / unstable / broken)
              │     ▼
              │ ┌──────────────────────┐
              │ │   Diagnosis Agent    │ ── Classifies root cause & generates repair plan (Phase 4)
              │ └──────────┬───────────┘
              │            │
              │            ▼
              │ ┌──────────────────────┐
              │ │    Healing Agent     │ ── Executes selector fixes & repairs (Phase 5)
              │ └──────────┬───────────┘
              │            │ (Re-scrape & validate)
              │            └───────────────┐
              ▼                            │
      ┌──────────────────────┐             │
      │ Final ScrapingResult │ ◄───────────┘
      └──────────────────────┘
```

---

## 3. LangGraph Workflow (Phase 4)

Phase 4 executes a conditional 5-node state graph workflow using **LangGraph**:

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

1. **`planner_node`**: Converts user query + URLs into a validated `ScrapingTask` using `ScrapingPlannerAgent` (Qwen3:8b).
2. **`scraper_node`**: Dispatches collection to Bright Data Scraper Studio or native HTTP fallback transport.
3. **`extraction_node`**: Converts raw HTML/text into structured records conforming to the task schema.
4. **`validation_node`**: Calculates field completeness, schema conformance, duplicate rate, anomalies, and mathematical health score.
5. **`diagnosis_node`** (Conditional): When quality degradation or structural failure is detected, `DiagnosisAgent` analyzes compact evidence, determines the root cause, and outputs an adaptive repair strategy.

---

## 4. Failure Diagnosis & Adaptive Repair Subsystem (`app/diagnosis/`)

### Root Cause Taxonomy:
`SELECTOR_DRIFT`, `DOM_STRUCTURE_CHANGE`, `SCRAPER_OUTPUT_MISSING`, `EXTRACTION_DEGRADATION`, `SCHEMA_MISMATCH`, `PAGINATION_FAILURE`, `RENDERING_FAILURE`, `CONTENT_FILTER_FAILURE`, `REGEX_PATTERN_FAILURE`, `TABLE_STRUCTURE_CHANGE`, `LLM_EXTRACTION_FAILURE`, `SOURCE_DATA_QUALITY`, `UNKNOWN`.

### Repair Strategy Taxonomy:
`REPAIR_CSS_SELECTORS`, `REPAIR_XPATH_SELECTORS`, `REPAIR_REGEX_PATTERN`, `REPAIR_TABLE_SCHEMA`, `REPAIR_EXTRACTION_SCHEMA`, `SWITCH_EXTRACTION_STRATEGY`, `REGENERATE_LLM_EXTRACTION_SCHEMA`, `ADJUST_CONTENT_CHUNKING`, `ADJUST_SEMANTIC_FILTERING`, `RECHECK_RAW_CONTENT`, `RETRY_SAME_CONFIGURATION`, `ESCALATE`.

### Crawl4AI-Inspired Adaptive Capabilities Clarification:
Crawl4AI provides useful concepts for content chunking, semantic cosine-similarity ranking, and LLM-friendly extraction strategies. It **does not** provide a built-in selector self-healing engine. Our self-healing pipeline combines validation metrics with `DiagnosisAgent` and `HealingAgent` to form an adaptive repair planning and execution architecture.

---

## 5. API Reference

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

**Diagnosed Failure Response:**
```json
{
  "task_id": "8f0be24c-b4db-4b68-80f4-5f54316d6342",
  "status": "partial",
  "records": [
    {
      "title": "Widget Pro",
      "price": null
    }
  ],
  "metadata": {
    "task_id": "8f0be24c-b4db-4b68-80f4-5f54316d6342",
    "record_count": 1,
    "health_score": 0.58,
    "quality_score": 0.62,
    "validation_status": "unstable",
    "diagnosis": {
      "diagnosis_status": "diagnosed",
      "root_cause": "SELECTOR_DRIFT",
      "confidence": 0.92,
      "affected_stage": "css_extraction",
      "affected_fields": ["price"],
      "evidence": [
        "Price field coverage dropped to 0% while HTML contains .current-price elements"
      ],
      "repair_strategy": "REPAIR_CSS_SELECTORS",
      "repair_targets": ["price"],
      "recommended_action": "REPAIR_EXTRACTION_SCHEMA"
    }
  },
  "error": "Degradation diagnosed: SELECTOR_DRIFT -> REPAIR_CSS_SELECTORS"
}
```

---

## 6. Running Tests

Run full test suite:
```powershell
python -m pytest tests -v
```

Run unit tests excluding live external integration:
```powershell
python -m pytest tests -k "not integration" -v
```
