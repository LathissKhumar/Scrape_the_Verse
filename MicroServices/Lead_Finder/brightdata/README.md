# Bright Data Scraper Studio & Dynamic Collector Management

Production-grade integration module for Bright Data Scraper Studio (Data Collector API and CLI) featuring dynamic scraper creation, intelligent collector reuse, asynchronous background generation, and self-healing hooks.

---

## Architecture Overview

```text
User Scraping Request (ScrapeTargetRequest)
                 ↓
      Scraper Orchestrator (BrightDataService)
                 ↓
Normalize Target URL + Compute SHA-256 Schema Fingerprint
                 ↓
      Scraper Registry (SQLite)
                 │
           Compatible?
          ↙           ↘
        YES            NO
         ↓              ↓
  Reuse Collector   Create Registry Record (status=CREATING)
  (status=READY)        ↓
         ↓          Spawn Background Creation Worker
  Return c_xxxxx        ↓
         │          Return Immediately (action=create, job_id=...)
         │              ↓
         │          Bright Data CLI (`scraper create <url> "<fields>"`)
         │              ↓
         │          Parse & Validate Collector ID (`c_xxxxx`)
         │              ↓
         └────────→ Persist Collector ID in Registry (status=READY)
                        ↓
                 Run Collector (`POST /scrapers/run`)
                        ↓
                 Structured JSON Records
```

---

## Module Structure

```text
app/brightdata/
├── __init__.py         # Package exports
├── adapter.py          # Legacy task adapter
├── client.py           # Subprocess CLI adapter & REST DCA client
├── exceptions.py       # Hierarchical error types
├── jobs.py             # Asynchronous background job manager (SQLite)
├── pipeline.py         # 2-Tier B2B IndiaMART discovery & company enrichment
├── registry.py         # Thread-safe SQLite registry with schema hashing & URL normalization
├── schemas.py          # Pydantic schemas and CollectorStatus enum
├── service.py          # High-level orchestrator (resolve, run, heal, execute)
└── README.md           # Documentation
```

---

## Key Components

### 1. Scraper Registry (`registry.py`)
- **Persistence**: Crash-resilient SQLite database with WAL mode and transaction locks (`app.crawler.db`).
- **URL Normalization**: Lowercases host, strips tracking query parameters (`utm_*`, `ref`, `fbclid`, `gclid`), sorts query parameters alphabetically.
- **Deterministic Schema Hash**: Canonical JSON sorting over requested field names and descriptions combined with normalized URL.
- **Idempotency**: Prevents duplicate concurrent scraper generation if an identical request is already in `CREATING` state.

### 2. Scraper Job Coordinator (`jobs.py`)
- **Non-blocking Execution**: Spawns background asyncio tasks for long-running collector creation.
- **State Tracking**: Manages lifecycle transitions `CREATING` → `READY` (persisting `c_xxxxxx`) or `CREATING` → `FAILED`.

### 3. Bright Data Client Adapter (`client.py`)
- **Safe Subprocess Execution**: Safe argument lists without `shell=True`, cross-platform binary resolution (`brightdata`, `bdata`, or `npx -p @brightdata/cli`).
- **Collector ID Validation**: Validates all returned IDs against the `^c_[a-zA-Z0-9]+$` pattern.
- **Observability**: Structured logs with safe identifiers, zero secret leakage.

### 4. Runtime Scraper Orchestrator (`service.py`)
- **`resolve_scraper(request)`**: Evaluates target URL and schema, returns `action="reuse"` if a compatible ready collector exists, or `action="create"` with an asynchronous background `job_id`.
- **`run_collector(collector_id, url)`**: Executes a ready collector and tracks `last_used_at` and `last_run_status`.
- **`heal_collector(collector_id, failure_description)`**: Invokes Bright Data self-healing CLI and updates health status.

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/scrapers/resolve` | Check registry and resolve collector reuse or start async creation |
| `GET` | `/scrapers/jobs/{job_id}` | Check status of background collector creation |
| `POST` | `/scrapers/run` | Execute a ready Bright Data collector against a URL |
| `POST` | `/scrapers/heal` | Self-heal a broken collector using description |
| `GET` | `/scrapers` | List registered collectors with optional status filter |
| `GET` | `/scrapers/{scraper_id}` | Retrieve collector metadata by internal ID or collector ID |

---

## Configuration

Set the following environment variables in `.env`:

```env
# Enable Bright Data features
BRIGHTDATA=True
BRIGHTDATA_API_KEY=your_brightdata_api_key

# Optional CLI and Registry overrides
BRIGHTDATA_CLI_COMMAND=brightdata
BRIGHTDATA_COMMAND_TIMEOUT=300.0
BRIGHTDATA_REGISTRY_DB_PATH=.brightdata_registry.sqlite
```
