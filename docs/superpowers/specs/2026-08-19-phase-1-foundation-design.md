# Phase 1: Multi-Agent Self-Healing Web Scraper Foundation & Scraping Planner Agent Design

## 1. Overview
This specification details the foundational architecture for Phase 1 of the Multi-Agent Self-Healing Web Scraping System.
The final system will accept plain-language user requests, orchestrate specialized sub-agents, execute resilient scraping via Bright Data Scraper Studio, extract structured records, validate quality, diagnose failures, and apply self-healing repair logic.

**Phase 1 Scope:**
- Provider-agnostic LLM client abstraction (`LLMClient`) backed by local Ollama (`qwen3:8b`).
- LangGraph-compatible state representation (`ScrapingGraphState`).
- Pydantic data schemas (`ScrapingRequest`, `ScrapingTask`, `ScrapingResult`).
- Functional `ScrapingPlannerAgent` that converts plain-language requests into structured `ScrapingTask` specifications without inventing URLs.
- Future agent skeletons with clean interfaces (`ScraperAgent`, `ExtractionAgent`, `ValidationAgent`, `DiagnosisAgent`, `HealingAgent`).
- Bright Data client abstraction stub (`BrightDataClient`).
- FastAPI REST service with `/`, `/health`, `/health/llm`, and `/parse-task` endpoints.

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
```

---

## 3. Core Architectural Rules
1. User supplies target URLs explicitly or within the plain-language query.
2. There is no URL discovery / search agent; no external search engines are queried.
3. The server generates `task_id = str(uuid4())` in Python and injects it into `ScrapingTask`.
4. Ollama `qwen3:8b` is accessed through `LLMClient` with markdown fence stripping.
