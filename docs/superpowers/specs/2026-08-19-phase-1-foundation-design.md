# Phase 1: Multi-Agent Self-Healing Web Scraper Foundation & Scraping Planner Agent Design

## 1. Overview
This specification details the foundational architecture for Phase 1 of the Multi-Agent Self-Healing Web Scraping System.
The final system will accept plain-language user requests, orchestrate specialized sub-agents, execute resilient scraping via Bright Data Scraper Studio, validate records, diagnose failures, and apply self-healing repair logic.

**Phase 1 Goal:** Build only the foundational infrastructure:
- Provider-agnostic LLM client abstraction (`LLMClient`) backed by local Ollama (`qwen3:8b`).
- LangGraph-compatible state representation (`ScrapingGraphState`).
- Pydantic data schemas (`ScrapingRequest`, `ScrapingTask`, `ScrapingResult`).
- Functional `ScrapingPlannerAgent` that converts plain-language requests into structured `ScrapingTask` specifications without inventing URLs or performing scraping.
- Future agent skeletons with clean interfaces (`ScraperAgent`, `ExtractionAgent`, `ValidationAgent`, `DiagnosisAgent`, `HealingAgent`).
- Bright Data client abstraction stub (`BrightDataClient`).
- FastAPI REST service with `/`, `/health`, `/health/llm`, and `/parse-task` endpoints.
- Comprehensive test suite and documentation.

---

## 2. Directory Structure

```
app/
├── agents/
│   ├── __init__.py
│   ├── base.py
│   ├── planner.py
│   ├── scraper.py
│   ├── extraction.py
│   ├── validation.py
│   ├── diagnosis.py
│   └── healing.py
├── graph/
│   ├── __init__.py
│   └── state.py
├── llm/
│   ├── __init__.py
│   ├── base.py
│   ├── exceptions.py
│   └── ollama_client.py
├── brightdata/
│   ├── __init__.py
│   └── client.py
├── models/
│   ├── __init__.py
│   └── schemas.py
├── config/
│   ├── __init__.py
│   ├── logging.py
│   └── settings.py
└── main.py
tests/
├── __init__.py
├── conftest.py
├── test_config.py
├── test_models.py
├── test_llm.py
├── test_graph_state.py
├── test_planner.py
├── test_brightdata.py
└── test_api.py
```

---

## 3. Detailed Component Specifications

### 3.1. Configuration (`app/config/settings.py` & `app/config/logging.py`)
- **Settings:** Uses `pydantic-settings` to load configuration from environment and `.env`.
  - `OLLAMA_BASE_URL`: `str = "http://localhost:11434"`
  - `OLLAMA_MODEL`: `str = "qwen3:8b"`
  - `OLLAMA_TIMEOUT_SECONDS`: `float = 60.0`
  - `BRIGHTDATA_API_KEY`: `str | None = None`
  - `BRIGHTDATA_COLLECTOR_ID`: `str | None = None`
  - `APP_ENV`: `str = "development"`
  - `LOG_LEVEL`: `str = "INFO"`
- **Startup Resilience:** Application boots even if Bright Data credentials are absent or Ollama is offline.
- **Logging:** Configured standard Python logging using format `[%(levelname)s] [%(name)s] %(message)s` with named loggers (`PLANNER`, `LLM`, `GRAPH`, `BRIGHTDATA`, `API`). Never logs API keys, secrets, or large scraped HTML payloads.

### 3.2. LLM Abstraction (`app/llm/`)
- **`LLMClient` Interface (`app/llm/base.py`):**
  - Abstract base class:
    - `async def invoke(self, prompt: str, system: str | None = None) -> str`
    - `def invoke_sync(self, prompt: str, system: str | None = None) -> str`
    - `async def check_health(self) -> dict[str, Any]`
    - Property `model_name -> str`
- **Exceptions (`app/llm/exceptions.py`):**
  - `LLMError`, `LLMConnectionError`, `LLMModelNotFoundError`, `LLMTimeoutError`, `LLMInvocationError`.
- **`OllamaClient` (`app/llm/ollama_client.py`):**
  - Implements `LLMClient` via `httpx.AsyncClient` and `httpx.Client`.
  - Uses Ollama `/api/generate` with `format: "json"` when requested / default JSON output.
  - Strips markdown code fences (````json ... ````) and cleans response strings.
  - Checks model presence via `/api/tags`.

### 3.3. Data Models (`app/models/schemas.py`)
- **`ScrapingRequest`:**
  - `query: str` (non-empty plain language scraping request)
  - `max_records: int | None = None` (must be > 0 if specified)
  - `target_urls: list[str] = Field(default_factory=list)` (validated as syntactically valid HTTP/HTTPS URLs)
  - *URL Ingestion*: Target URLs can be provided explicitly in `target_urls` OR embedded in the plain-language `query`.
- **`ScrapingTask`:**
  - `task_id: str` (UUID generated server-side in Python)
  - `objective: str`
  - `target_urls: list[str] = Field(default_factory=list)`
  - `fields: list[str] = Field(default_factory=list)`
  - `output_schema: dict[str, Any] | None = None`
  - `max_records: int | None = None`
  - `constraints: list[str] = Field(default_factory=list)`
  - `source_requirements: list[str] = Field(default_factory=list)`
- **`ScrapingResult`:**
  - `status: Literal["success", "partial", "failed"]`
  - `records: list[dict[str, Any]] = Field(default_factory=list)`
  - `metadata: dict[str, Any] = Field(default_factory=dict)`
  - `error: str | None = None`

### 3.4. LangGraph State (`app/graph/state.py`)
- **`ScrapingGraphState(TypedDict, total=False)`:**
  - `task_id: str`
  - `original_user_query: str`
  - `scraping_task: ScrapingTask | None`
  - `target_urls: list[str]`
  - `scraper_id: str | None`
  - `scraper_version: str | None`
  - `scraper_code: str | None`
  - `raw_results: list[dict[str, Any]] | None`
  - `extracted_results: list[dict[str, Any]] | None`
  - `validation_result: dict[str, Any] | None`
  - `failure: dict[str, Any] | None`
  - `repair_attempt: int`
  - `final_output: ScrapingResult | None`
- *Note:* Graph execution is deferred to Phase 2; Phase 1 defines the state structure only.

### 3.5. Agent Architecture (`app/agents/`)
- **`BaseAgent` (`app/agents/base.py`):** Minimal base class with agent `name` and standard logger.
- **`ScrapingPlannerAgent` (`app/agents/planner.py`):**
  - Converts `ScrapingRequest` + server-generated `task_id` into a structured `ScrapingTask`.
  - Merges URLs supplied in `target_urls` with any URLs found in the `query` text without inventing URLs.
  - Server generates `task_id = str(uuid4())` and injects it; the LLM is not prompted to generate `task_id`.
  - Injects strict planner prompt:
    - Never invent URLs or facts.
    - Never search the web or scrape.
    - Preserve user-provided URLs verbatim.
    - Extract requested fields and infer `output_schema` where evident.
    - Return JSON only.
  - Validates output using Pydantic `ScrapingTask`.
- **Future Agent Skeletons:**
  - `ScraperAgent` (`app/agents/scraper.py`): Future dispatch to Bright Data.
  - `ExtractionAgent` (`app/agents/extraction.py`): Future LLM-based structured extraction.
  - `ValidationAgent` (`app/agents/validation.py`): Future data validation against schema and rules.
  - `DiagnosisAgent` (`app/agents/diagnosis.py`): Future failure analysis and root cause determination.
  - `HealingAgent` (`app/agents/healing.py`): Future scraper code repair generation.

### 3.6. Bright Data Client Abstraction (`app/brightdata/client.py`)
- Defines `BrightDataClient`:
  - `async def trigger_scraper(self, collector_id: str, inputs: list[dict[str, Any]]) -> str`
  - `async def get_job_status(self, job_id: str) -> dict[str, Any]`
  - `async def fetch_results(self, job_id: str) -> list[dict[str, Any]]`
- Phase 1 raises `NotImplementedError("Bright Data execution will be implemented in Phase 2.")`.

### 3.7. FastAPI Application (`app/main.py`)
- `GET /` -> `{"service": "self-healing-scraper", "status": "running", "phase": 1}`
- `GET /health` -> Basic service health and configuration summary.
- `GET /health/llm` -> Ollama connectivity and `qwen3:8b` model availability (lightweight tag check, no inference).
- `POST /parse-task` -> Ingests `ScrapingRequest`, assigns UUID `task_id`, invokes `ScrapingPlannerAgent`, returns `{"task_id": "...", "scraping_task": {...}}`.

---

## 4. Verification & Testing Strategy
- **`test_config.py`:** Configuration defaults, environment overrides, logger initialization.
- **`test_models.py`:** `ScrapingRequest` (URL validation, empty checks), `ScrapingTask`, `ScrapingResult`.
- **`test_llm.py`:** Mocked httpx calls for successful output, markdown fence stripping, timeouts, connection errors, missing model errors.
- **`test_graph_state.py`:** `ScrapingGraphState` field types and default initialization.
- **`test_planner.py`:** `ScrapingPlannerAgent` with mocked LLM output (URL preservation, schema generation, malformed JSON handling, query vs target_urls merging).
- **`test_brightdata.py`:** Verifies `BrightDataClient` raises `NotImplementedError`.
- **`test_api.py`:** FastAPI TestClient tests for `GET /`, `GET /health`, `GET /health/llm`, and `POST /parse-task`.
- **Integration Tests:** `@pytest.mark.integration` test against local Ollama `qwen3:8b`.
