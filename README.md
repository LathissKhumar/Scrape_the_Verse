# Self-Healing Multi-Agent Web Scraping System

A plain-language, multi-agent, self-healing web scraping framework powered by **LangGraph**, **Ollama**, local **Qwen3:8b**, **Bright Data Scraper Studio**, a modular **Extraction Engine**, and a deterministic **Validation Engine**.

---

## 1. Project Purpose & Overview

Traditional web scraping pipelines frequently break due to dynamic DOM structures, anti-bot protections, pagination changes, and selector drift. This project implements an autonomous, self-healing scraping system where:
1. Users submit web scraping objectives in **plain, natural language** along with target URLs (either supplied in structured lists or referenced within the prompt).
2. A **Scraping Planner Agent** interprets the human objective into a deterministic scraping task specification.
3. Sub-agents coordinate across the lifecycle: dispatching crawl jobs to **Bright Data**, extracting structured records via our modular extraction engine, validating quality against schemas and historical baselines, diagnosing runtime failures, and executing LLM-guided self-healing code repairs.

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
      │    Scraper Agent     │ ── Dispatches crawl jobs to Bright Data Scraper Studio
      └──────────┬───────────┘
                 │
                 ▼
      ┌──────────────────────┐
      │   Extraction Agent   │ ── Modular Extraction Engine (CSS/XPath/Regex/Table/LLM)
      └──────────┬───────────┘
                 │
                 ▼
      ┌──────────────────────┐
      │   Validation Agent   │ ── Deterministic Validation & Health Scoring (Phase 3)
      └──────────┬───────────┘
                 │
           ┌─────┴─────┐
           │ Healthy?  │
           └──┬─────┬──┘
          YES │     │ NO
              │     ▼
              │ ┌──────────────────────┐
              │ │   Diagnosis Agent    │ ── Classifies error & identifies root cause (Phase 4)
              │ └──────────┬───────────┘
              │            │
              │            ▼
              │ ┌──────────────────────┐
              │ │    Healing Agent     │ ── Generates selector fixes & repairs (Phase 5)
              │ └──────────┬───────────┘
              │            │ (Re-scrape & validate)
              │            └───────────────┐
              ▼                            │
      ┌──────────────────────┐             │
      │ Final ScrapingResult │ ◄───────────┘
      └──────────────────────┘
```

---

## 3. LangGraph Workflow (Phase 3)

Phase 3 executes a compiled 4-node state graph workflow using **LangGraph**:

```
START ──► [planner_node] ──► [scraper_node] ──► [extraction_node] ──► [validation_node] ──► END
```

1. **`planner_node`**: Converts `original_user_query` + `target_urls` into a validated `ScrapingTask` using `ScrapingPlannerAgent` (backed by local `qwen3:8b`).
2. **`scraper_node`**: Formats inputs via the Bright Data adapter, dispatches to `BrightDataClient`, polls for completion, and sets `raw_results`.
3. **`extraction_node`**: Executes `ExtractionAgent` and `ExtractionEngine` to convert raw HTML/text into structured records.
4. **`validation_node`**: Executes `ValidationAgent` and `ValidationEngine` to evaluate data completeness, schema conformance, URL/type validity, duplicate rates, anomalies, and mathematical health/quality scores.

---

## 4. Deterministic Validation Subsystem (`app/validation/`)

The validation subsystem performs 100% deterministic, non-LLM evaluations:

### Health Score Formula:
$$\text{Health Score} = 0.20 \times \text{Schema} + 0.20 \times \text{Completeness} + 0.15 \times \text{Count} + 0.10 \times \text{Type} + 0.10 \times \text{URL} + 0.10 \times \text{Dup} + 0.15 \times \text{Consistency}$$

### Health Categories:
- **`healthy`** (`0.85 - 1.00`): Pipeline operating cleanly.
- **`degraded`** (`0.65 - 0.849`): Minor coverage drops or mild duplicate issues.
- **`unstable`** (`0.40 - 0.649`): Moderate failure, high duplicate spike, or significant field loss.
- **`broken`** (`0.00 - 0.399`): Zero records, total schema mismatch, or structural collapse.

### Failure Taxonomy:
`EMPTY_RESULTS`, `SCRAPER_OUTPUT_MISSING`, `EXTRACTION_DEGRADATION`, `SCHEMA_MISMATCH`, `LOW_FIELD_COVERAGE`, `HIGH_DUPLICATE_RATE`, `INVALID_URLS`, `INVALID_FIELD_TYPES`, `LOW_RECORD_COUNT`, `UNEXPECTED_STRUCTURE`.

---

## 5. API Reference

### `POST /scrape` (Execute Full Pipeline)

**Request:**
```json
{
  "query": "Scrape company name, website, and employee count from the provided website",
  "target_urls": [
    "https://example.com/directory"
  ],
  "max_records": 50
}
```

**Healthy Response:**
```json
{
  "task_id": "8f0be24c-b4db-4b68-80f4-5f54316d6342",
  "status": "success",
  "records": [
    {
      "name": "Acme Corp",
      "website": "https://acme.example.com",
      "employees": 150
    }
  ],
  "metadata": {
    "task_id": "8f0be24c-b4db-4b68-80f4-5f54316d6342",
    "record_count": 1,
    "health_score": 0.96,
    "quality_score": 0.94,
    "validation_status": "healthy",
    "anomalies": [],
    "validation": {
      "field_coverage": {
        "name": 1.0,
        "website": 1.0,
        "employees": 1.0
      },
      "duplicate_rate": 0.0,
      "url_valid_rate": 1.0,
      "schema_valid_rate": 1.0
    }
  },
  "error": null
}
```

**Degraded/Broken Response:**
```json
{
  "task_id": "8f0be24c-b4db-4b68-80f4-5f54316d6342",
  "status": "partial",
  "records": [...],
  "metadata": {
    "health_score": 0.52,
    "quality_score": 0.58,
    "validation_status": "unstable",
    "anomalies": [
      "Critical coverage collapse for field 'employees' (15.0%)."
    ]
  },
  "error": "Validation detected quality degradation: health_score=0.52"
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
