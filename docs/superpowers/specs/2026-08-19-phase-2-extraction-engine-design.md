# Phase 2: LangGraph Orchestration, Bright Data Client & Modular Extraction Engine Design

## 1. Overview
Phase 2 activates the first real, executable scraping and structured extraction pipeline in **Scrape_the_Verse**:
1. Connects **Bright Data Scraper Studio** as the production web scraping layer with safe async polling.
2. Builds an in-house modular **Extraction Engine** inspired by Crawl4AI techniques (CSS, XPath, Regex, Table scoring, Content Chunking, Semantic Relevance Filtering, LLM Qwen3:8b, Deduplication, Strategy Selection & Fallback) without third-party framework lock-in.
3. Orchestrates the end-to-end flow via a 3-node **LangGraph** workflow: `START -> planner -> scraper -> extraction -> END`.
4. Exposes the `POST /scrape` REST endpoint on FastAPI.

---

## 2. Extraction Engine Architecture (`app/extraction/`)

```
Raw Scraped Content (HTML / Text / Payloads)
                      │
                      ▼
            ┌───────────────────┐
            │ Extraction Engine │
            └─────────┬─────────┘
                      │
   ┌──────────────────┼──────────────────┬──────────────────┐
   │ (Selectors)      │ (Pattern)        │ (Table)          │ (Unstructured)
   ▼                  ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌───────────────────┐
│ CSS / XPath  │  │ Regex Parser │  │ Table Parser │  │ Content Chunking  │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └─────────┬─────────┘
       │                 │                 │                    │
       │                 │                 │                    ▼
       │                 │                 │          ┌───────────────────┐
       │                 │                 │          │ Semantic Ranking  │
       │                 │                 │          └─────────┬─────────┘
       │                 │                 │                    │ (Top-k Chunks)
       │                 │                 │                    ▼
       │                 │                 │          ┌───────────────────┐
       │                 │                 │          │ LLM (Qwen3:8b)    │
       │                 │                 │          └─────────┬─────────┘
       │                 │                 │                    │
       ▼                 ▼                 ▼                    ▼
   ┌──────────────────────────────────────────────────────────────┐
   │                   Deduplication & Schema Alignment          │
   └──────────────────────────────┬───────────────────────────────┘
                                  │
                                  ▼
                        Structured Records
```

---

## 3. LangGraph Workflow

```
START ──► [planner_node] ──► [scraper_node] ──► [extraction_node] ──► END
```

- **`planner_node`**: Invokes `ScrapingPlannerAgent` (Qwen3:8b) to parse requests into `ScrapingTask`.
- **`scraper_node`**: Formats inputs via `app/brightdata/adapter.py`, triggers Bright Data Scraper Studio, and polls for raw results.
- **`extraction_node`**: Invokes `ExtractionAgent` and `ExtractionEngine` to convert raw HTML/text into clean structured records.

---

## 4. Verification Strategy
- Unit tests for every extraction strategy (`test_extraction_css.py`, `test_extraction_xpath.py`, `test_extraction_regex.py`, `test_extraction_tables.py`, `test_extraction_chunking.py`, `test_extraction_semantic.py`, `test_extraction_llm.py`, `test_extraction_dedup.py`, `test_extraction_engine.py`, `test_extraction_agent.py`).
- Workflow state machine tests (`test_graph_workflow.py`).
- API endpoint integration tests (`test_api.py`).
