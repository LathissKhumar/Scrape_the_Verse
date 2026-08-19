# Self-Healing Multi-Agent Web Scraping System

A plain-language, multi-agent, self-healing web scraping framework powered by **LangGraph**, **Ollama**, local **Qwen3:8b**, **Bright Data Scraper Studio**, and an in-house modular **Extraction Engine**.

---

## 1. Project Purpose & Overview

Traditional web scraping pipelines frequently break due to dynamic DOM structures, anti-bot protections, pagination changes, and selector drift. This project implements an autonomous, self-healing scraping system where:
1. Users submit web scraping objectives in **plain, natural language** along with target URLs (either supplied in structured lists or referenced within the prompt).
2. A **Scraping Planner Agent** interprets the human objective into a deterministic scraping task specification.
3. Sub-agents coordinate across the lifecycle: dispatching crawl jobs to **Bright Data**, extracting structured records via our modular extraction engine, validating quality against schemas, diagnosing runtime failures, and executing LLM-guided self-healing code repairs.

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
      │   Extraction Agent   │ ── Modular Extraction Engine (CSS / XPath / Regex / Table / Semantic / LLM)
      └──────────┬───────────┘
                 │
                 ▼
      ┌──────────────────────┐
      │   Validation Agent   │ ── Validates schema, completeness & constraints (Phase 4)
      └──────────┬───────────┘
                 │
           ┌─────┴─────┐
           │ Healthy?  │
           └──┬─────┬──┘
          YES │     │ NO
              │     ▼
              │ ┌──────────────────────┐
              │ │   Diagnosis Agent    │ ── Classifies error & identifies root cause (Phase 5)
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

## 3. LangGraph Workflow (Phase 2)

Phase 2 executes a 3-node compiled state graph workflow using **LangGraph**:

```
START ──► [planner_node] ──► [scraper_node] ──► [extraction_node] ──► END
```

1. **`planner_node`**: Converts `original_user_query` + `target_urls` into a validated `ScrapingTask` using `ScrapingPlannerAgent` (backed by local `qwen3:8b`).
2. **`scraper_node`**: Formats inputs via the Bright Data adapter, dispatches to `BrightDataClient`, polls for completion, and sets `raw_results`.
3. **`extraction_node`**: Executes `ExtractionAgent` and `ExtractionEngine` to convert raw HTML/text into structured records conforming to task schema, setting `final_output: ScrapingResult`.

---

## 4. Modular Extraction Engine (`app/extraction/`)

The proprietary extraction engine provides comprehensive extraction capabilities without third-party web scraper framework lock-in:

- **CSS Extraction** (`css.py`): Deterministic element and attribute extraction via BeautifulSoup.
- **XPath Extraction** (`xpath.py`): Relative and container XPath extraction via `lxml.html`.
- **Regex Extraction** (`regex.py`): Pattern-based extraction for emails, phone numbers, prices, URLs, dates, and custom patterns.
- **HTML Table Extraction** (`tables.py`): Heuristic data table detection, scoring, header alignment, and structured row extraction.
- **Content Chunking** (`chunking.py`): Sentence and paragraph-boundary chunking with configurable overlap and context preservation.
- **Semantic Filtering** (`semantic.py`): Cosine-similarity ranking of chunks against task objectives using TF-IDF / vector embeddings to send only relevant content to the LLM.
- **LLM Extraction** (`llm.py`): Schema-constrained structured extraction and table fallback using local `qwen3:8b`.
- **Record Deduplication** (`dedup.py`): URL and composite-hash deduplication.
- **Strategy Selector & Cascade** (`engine.py`): Prioritizes deterministic strategies (CSS/XPath/Regex/Table) before falling back to Qwen3:8b to conserve compute.

---

## 5. Configuration

Create `.env` from `.env.example`:
```env
# Ollama Local LLM Settings
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:8b
OLLAMA_TIMEOUT_SECONDS=60.0

# Bright Data Configuration
BRIGHTDATA_API_KEY=your_api_key_here
BRIGHTDATA_COLLECTOR_ID=c_xxxxxxxxxxxxxxxx

# Application Settings
APP_ENV=development
LOG_LEVEL=INFO
```

---

## 6. Running the Application

```powershell
python run.py
```
Or with uvicorn:
```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 7. API Reference

### 1. `POST /scrape` (Execute End-to-End Pipeline)

**Request:**
```json
{
  "query": "Scrape product names, prices and ratings from the provided website",
  "target_urls": [
    "https://example.com/products"
  ],
  "max_records": 20
}
```

**Response (Success):**
```json
{
  "task_id": "8f0be24c-b4db-4b68-80f4-5f54316d6342",
  "status": "success",
  "records": [
    {
      "product_name": "Product Alpha",
      "price": "$19.99",
      "rating": 4.8
    }
  ],
  "metadata": {
    "task_id": "8f0be24c-b4db-4b68-80f4-5f54316d6342",
    "record_count": 1,
    "extraction_strategy": "css",
    "fallback_used": false
  },
  "error": null
}
```

### 2. `POST /parse-task` (Planner Parser Only)
Converts human natural language requests into structured `ScrapingTask` without triggering scraping.

### 3. `GET /health` & `GET /health/llm`
Inspect service health and local Ollama model availability.

---

## 8. Running Tests

Run full test suite:
```powershell
python -m pytest tests -v
```

Run unit tests excluding live external integration:
```powershell
python -m pytest tests -k "not integration" -v
```
