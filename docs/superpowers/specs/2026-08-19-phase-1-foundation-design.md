# Phase 1: Multi-Agent Self-Healing Web Scraper Foundation & Task Parser Design

## 1. Overview
This specification details the foundational architecture for Phase 1 of the Multi-Agent Self-Healing Web Scraping System.
The system will eventually accept plain-language scraping goals, orchestrate multiple specialized sub-agents, execute resilient scraping via Bright Data Scraper Studio, detect runtime failures, and leverage LLMs to diagnose and repair broken scraping logic.

Phase 1 focuses exclusively on establishing a clean, modular foundation:
- Provider-agnostic LLM client abstractions (starting with local Ollama running `qwen3:8b`).
- Robust Pydantic data schemas and LangGraph state representations.
- Agent skeletons for the entire multi-agent lifecycle with a functional `ManagerAgent` for plain-language query parsing into structured `ScrapingTask` specifications.
- FastAPI REST service with health, status, and `/parse-task` endpoints.
- Bright Data client abstraction stub.
- Comprehensive test harness (mocked unit tests and isolated integration tests).

---

## 2. Architecture & Directory Layout

```
self-healing-scraper/
├── app/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── manager.py
│   │   ├── discovery.py
│   │   ├── scraper.py
│   │   ├── extraction.py
│   │   ├── validation.py
│   │   ├── diagnosis.py
│   │   └── healing.py
│   ├── graph/
│   │   ├── __init__.py
│   │   └── state.py
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── exceptions.py
│   │   └── ollama_client.py
│   ├── brightdata/
│   │   ├── __init__.py
│   │   └── client.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── logging.py
│   │   └── settings.py
│   └── main.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_llm.py
│   ├── test_models.py
│   └── test_api.py
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
└── run.py
```

---

## 3. Component Specifications

### 3.1. Configuration (`app/config/settings.py` & `app/config/logging.py`)
- **Settings:** Uses `pydantic-settings` to parse configuration from `.env` and environment variables.
  - `OLLAMA_BASE_URL`: `str = "http://localhost:11434"`
  - `OLLAMA_MODEL`: `str = "qwen3:8b"`
  - `OLLAMA_TIMEOUT_SECONDS`: `float = 60.0`
  - `BRIGHTDATA_API_KEY`: `Optional[str] = None`
  - `BRIGHTDATA_COLLECTOR_ID`: `Optional[str] = None`
  - `APP_ENV`: `str = "development"`
  - `LOG_LEVEL`: `str = "INFO"`
- **Startup Grace:** Empty Bright Data credentials will not block application boot.
- **Logging:** Configured standard Python logging with structured formatting: `[%(levelname)s] [%(name)s] %(message)s`.

### 3.2. LLM Provider Abstraction (`app/llm/`)
- **`LLMClient` Interface (`app/llm/base.py`):**
  - Defines an abstract base class / protocol with:
    - `async def invoke(self, prompt: str, system: Optional[str] = None) -> str`
    - `def invoke_sync(self, prompt: str, system: Optional[str] = None) -> str`
    - `async def check_health(self) -> dict[str, Any]`
    - Property `model_name -> str`
- **`OllamaClient` (`app/llm/ollama_client.py`):**
  - Implements `LLMClient` via `httpx.AsyncClient` targeting Ollama's HTTP API.
  - Supports `/api/generate` (or `/api/chat`) with JSON mode enforcement when structured outputs are requested.
  - Custom exceptions: `LLMError`, `LLMConnectionError`, `LLMModelNotFoundError`, `LLMTimeoutError`.
  - Robust JSON parsing fallback: strips markdown code fences (` ```json ... ``` `) and cleans trailing commas or whitespace.

### 3.3. Data Models (`app/models/schemas.py`)
- **`ScrapingRequest`:**
  - `query: str` (non-empty plain-language instruction)
  - `max_records: Optional[int] = None`
  - `target_urls: Optional[list[str]] = Field(default_factory=list)`
- **`ScrapingTask`:**
  - `objective: str` (concise summary of scraping goal)
  - `fields: list[str]` (target attributes to extract, e.g. `["company_name", "website", "founder"]`)
  - `target_urls: list[str] = Field(default_factory=list)`
  - `max_records: Optional[int] = None`
  - `constraints: list[str] = Field(default_factory=list)`
- **`ScrapingResult`:**
  - `status: str` (`success`, `failed`, `partial`)
  - `records: list[dict[str, Any]] = Field(default_factory=list)`
  - `data: Optional[dict[str, Any]] = None`
  - `error: Optional[str] = None`

### 3.4. LangGraph State (`app/graph/state.py`)
- **`ScraperGraphState(TypedDict, total=False)`:**
  - `original_user_query: str`
  - `scraping_task: ScrapingTask`
  - `target_urls: list[str]`
  - `raw_results: list[dict[str, Any]]`
  - `extracted_results: list[dict[str, Any]]`
  - `validation_result: dict[str, Any]`
  - `failure: Optional[dict[str, Any]]`
  - `repair_attempt: int`
  - `final_output: ScrapingResult`

### 3.5. Agent Subsystems (`app/agents/`)
- **`BaseAgent` (`app/agents/base.py`):** Abstract class with `name` and standardized execution method.
- **`ManagerAgent` (`app/agents/manager.py`):**
  - Connects to `LLMClient`.
  - Converts plain-language user requests to `ScrapingTask` instances.
  - Injects strict prompt instructions requiring valid JSON output conforming to the `ScrapingTask` schema.
  - Validates output using Pydantic.
- **Agent Skeletons (Future Phase Stubs with TODO comments & method contracts):**
  - `DiscoveryAgent`: Identifies candidate URLs given a `ScrapingTask`.
  - `ScraperAgent`: Dispatches crawl jobs to Bright Data client.
  - `ExtractionAgent`: Normalizes raw HTML/JSON into structured entities.
  - `ValidationAgent`: Validates record counts, non-empty attributes, and constraint adherence.
  - `DiagnosisAgent`: Diagnoses failures (e.g. anti-bot blocking, selector drift, schema mismatch).
  - `HealingAgent`: Formulates LLM-driven repair plans.

### 3.6. Bright Data Client (`app/brightdata/client.py`)
- `BrightDataClient` abstraction supporting future API calls:
  - `async def trigger_scraper(self, collector_id: str, inputs: list[dict[str, Any]]) -> str`
  - `async def get_job_status(self, job_id: str) -> dict[str, Any]`
  - `async def fetch_results(self, job_id: str) -> list[dict[str, Any]]`
- Phase 1 stubs raise `NotImplementedError` with explicit future implementation notes.

### 3.7. FastAPI Application (`app/main.py`)
- **Endpoints:**
  - `GET /`: `{"service": "self-healing-scraper", "status": "running", "phase": 1}`
  - `GET /health`: Overall system readiness and configuration status.
  - `GET /health/llm`: Inspects Ollama connectivity and model availability (`qwen3:8b`) via `/api/tags`.
  - `POST /parse-task`: Accepts `ScrapingRequest`, invokes `ManagerAgent`, returns validated `ScrapingTask`.
- **Exception Handlers:**
  - `LLMConnectionError` -> HTTP 503 (Ollama unreachable)
  - `LLMModelNotFoundError` -> HTTP 503 (Model not pulled)
  - `ValueError` / `ValidationError` -> HTTP 422 / HTTP 400

---

## 4. Verification & Testing Strategy
1. **Model & Schema Tests (`tests/test_models.py`):**
   - Validates `ScrapingRequest`, `ScrapingTask`, and `ScrapingResult` instantiation, field defaults, and validation errors.
2. **LLM Client Unit Tests (`tests/test_llm.py`):**
   - Mocked httpx calls testing successful responses, timeouts, connection errors, and markdown cleanup.
   - Optional `@pytest.mark.integration` test targeting live Ollama `qwen3:8b`.
3. **Manager Agent & API Tests (`tests/test_api.py`):**
   - Mocked LLM responses asserting `POST /parse-task` returns valid `ScrapingTask` structures.
   - Assertions for `GET /`, `GET /health`, and `GET /health/llm`.
