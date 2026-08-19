# Self-Healing Multi-Agent Web Scraping System

A plain-language, multi-agent, self-healing web scraping framework powered by **LangGraph**, **Ollama**, local **Qwen3:8b**, and **Bright Data Scraper Studio**.

---

## 1. Project Purpose & Overview

Traditional web scraping pipelines frequently break due to dynamic DOM structures, anti-bot protections, pagination changes, and selector drift. This project implements an autonomous, self-healing scraping system where:
1. Users submit web scraping objectives in **plain, natural language** along with target URLs (either supplied in structured lists or referenced within the prompt).
2. A **Scraping Planner Agent** interprets the human objective into a deterministic scraping task specification.
3. Sub-agents coordinate across the lifecycle: dispatching crawl jobs to **Bright Data**, extracting structured data, validating quality against schemas, diagnosing runtime failures, and executing LLM-guided self-healing code repairs.

> [!IMPORTANT]
> **No URL Discovery / Search Engine Agent**: The system operates exclusively on URLs provided explicitly by the user or identified in the user's natural language request. The system never invents URLs or uses external search engines.

---

## 2. Architecture & Multi-Agent Lifecycle

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
      │    Scraper Agent     │ ── Dispatches crawl jobs (Bright Data in Phase 2)
      └──────────┬───────────┘
                 │
                 ▼
      ┌──────────────────────┐
      │   Extraction Agent   │ ── Normalizes raw payloads into structured records
      └──────────┬───────────┘
                 │
                 ▼
      ┌──────────────────────┐
      │   Validation Agent   │ ── Validates schema, completeness & constraints
      └──────────┬───────────┘
                 │
           ┌─────┴─────┐
           │ Healthy?  │
           └──┬─────┬──┘
          YES │     │ NO
              │     ▼
              │ ┌──────────────────────┐
              │ │   Diagnosis Agent    │ ── Classifies error & identifies root cause
              │ └──────────┬───────────┘
              │            │
              │            ▼
              │ ┌──────────────────────┐
              │ │    Healing Agent     │ ── Generates selector fixes & repairs
              │ └──────────┬───────────┘
              │            │ (Re-scrape & validate)
              │            └───────────────┐
              ▼                            │
      ┌──────────────────────┐             │
      │ Final ScrapingResult │ ◄───────────┘
      └──────────────────────┘
```

---

## 3. Why LangGraph & Architectural Separation

- **Why LangGraph**: LangGraph provides cyclical state graph orchestration, allowing workflows to loop dynamically (e.g., `Scraper -> Validation -> Diagnosis -> Healing -> Scraper`) with checkpointing, fault tolerance, and clear boundary isolation between steps.
- **Why Bright Data is Separated**: Bright Data provides battle-tested web unlocking, rotating proxy networks, and JavaScript rendering. By decoupling the scraping infrastructure via `BrightDataClient`, our agents focus purely on planning, data normalization, schema validation, and intelligent self-healing without hardcoding scraping transport logic.
- **Why LLM Provider Abstraction**: LLM calls route through `LLMClient`, allowing seamless transitions between local models (Ollama with `qwen3:8b`) and remote LLMs (Claude, OpenAI, Gemini) without altering agent interfaces.

---

## 4. Phase 1 Scope vs. Phase 2 Roadmap

### Phase 1 Scope (Current Foundation):
- [x] Provider-agnostic LLM interface (`LLMClient`) and local `OllamaClient` with markdown fence stripping and error normalization.
- [x] LangGraph-compatible state representation (`ScrapingGraphState`).
- [x] Pydantic models with HTTP/HTTPS URL syntax validation (`ScrapingRequest`, `ScrapingTask`, `ScrapingResult`).
- [x] Fully functional `ScrapingPlannerAgent` converting plain language to validated `ScrapingTask` instances without inventing URLs.
- [x] Agent skeletons with method contracts for `ScraperAgent`, `ExtractionAgent`, `ValidationAgent`, `DiagnosisAgent`, and `HealingAgent`.
- [x] Bright Data client abstraction stub (`BrightDataClient`) with `NotImplementedError` guardrails.
- [x] FastAPI service (`GET /`, `GET /health`, `GET /health/llm`, `POST /parse-task`).
- [x] Full unit and live integration test suite with 100% pass rate.

### Phase 2+ Roadmap:
- **Phase 2**: Connect `BrightDataClient` to live Bright Data Scraper Studio API and implement `ScraperAgent`.
- **Phase 3**: Implement `ExtractionAgent` for LLM-assisted HTML-to-JSON normalization.
- **Phase 4**: Implement `ValidationAgent` for data completeness, type checks, and constraint validation.
- **Phase 5**: Implement `DiagnosisAgent` and `HealingAgent` to enable self-healing loops for selector drift and blocking.

---

## 5. Prerequisites & Local LLM Setup

### 1. Install Ollama
Download and install Ollama from [ollama.com](https://ollama.com).

### 2. Pull Qwen3:8b Model
```powershell
ollama pull qwen3:8b
```

### 3. Verify Ollama is Running
```powershell
curl http://localhost:11434/api/tags
```

---

## 6. Installation & Configuration

### 1. Clone & Install Dependencies
```powershell
git clone https://github.com/Balaji-1206/Scrape_the_Verse.git
cd Scrape_the_Verse
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` (optional defaults will be used if omitted):
```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:8b
OLLAMA_TIMEOUT_SECONDS=60.0

# Optional in Phase 1
BRIGHTDATA_API_KEY=
BRIGHTDATA_COLLECTOR_ID=

APP_ENV=development
LOG_LEVEL=INFO
```

---

## 7. Running the Service

Start the FastAPI application via `run.py` or `uvicorn`:
```powershell
python run.py
```
Or directly:
```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 8. API Reference & Examples

### 1. Service Root
**`GET /`**
```json
{
  "service": "self-healing-scraper",
  "status": "running",
  "phase": 1
}
```

### 2. General Health Check
**`GET /health`**
```json
{
  "status": "healthy",
  "environment": "development",
  "ollama_base_url": "http://localhost:11434",
  "ollama_model": "qwen3:8b",
  "brightdata_configured": false
}
```

### 3. LLM Connectivity Check
**`GET /health/llm`** (lightweight tag inspection, does not run inference)
```json
{
  "available": true,
  "model_name": "qwen3:8b",
  "model_installed": true,
  "available_models": ["qwen3:8b", ...]
}
```

### 4. Parse Scraping Task
**`POST /parse-task`**

**Request (Explicit URLs):**
```json
{
  "query": "Scrape https://example.com/products and collect product name, price and rating",
  "target_urls": [
    "https://example.com/products"
  ],
  "max_records": 100
}
```

**Request (URL inside query string):**
```json
{
  "query": "Scrape all blog posts from https://news.example.com/blog and extract article title and publication date"
}
```

**Response:**
```json
{
  "task_id": "8f0be24c-b4db-4b68-80f4-5f54316d6342",
  "scraping_task": {
    "task_id": "8f0be24c-b4db-4b68-80f4-5f54316d6342",
    "objective": "Scrape product names, prices and ratings from the provided website",
    "target_urls": [
      "https://example.com/products"
    ],
    "fields": [
      "product_name",
      "price",
      "rating"
    ],
    "output_schema": {
      "product_name": "string",
      "price": "string",
      "rating": "number"
    },
    "max_records": 100,
    "constraints": [],
    "source_requirements": []
  }
}
```

---

## 9. Running Tests

Run the complete test suite (unit and mocked tests run offline without external dependencies):
```powershell
python -m pytest tests -v
```

Run integration tests against live Ollama:
```powershell
python -m pytest tests -m integration -v
```
