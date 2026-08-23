# SDR Microservice & Lead Pipeline Integration Implementation Plan

**Spec Reference**: `docs/superpowers/specs/2026-08-23-sdr-orchestrator-and-pipeline-integration-design.md`  
**Target Services**: SDR Microservice (:8081), Lead Finder (:8000), Lead Manager (:8082)

---

## Proposed Changes & Files

### 1. SDR Microservice Architecture (`MicroServices/SDR/`)
- `[NEW]` [opportunity_builder.py](file:///home/lathiss/Projects/Scrape_the_Verse/MicroServices/SDR/opportunity_builder.py): Synthesizes raw crawl/audit outputs into structured `Opportunity` objects with evidence and recommendations.
- `[NEW]` [orchestrator.py](file:///home/lathiss/Projects/Scrape_the_Verse/MicroServices/SDR/orchestrator.py): High-level SDR orchestrator running LibreCrawl + SEO Analyzers + Opportunity Builder, with direct dispatch to Lead Manager.
- `[NEW]` [server.py](file:///home/lathiss/Projects/Scrape_the_Verse/MicroServices/SDR/server.py): FastAPI microservice on port 8081 with `/api/v1/audit`, `/api/v1/audit/dispatch-to-lead-manager`, `/health`, `/ready`, and A2A discovery.
- `[NEW]` [run.py](file:///home/lathiss/Projects/Scrape_the_Verse/MicroServices/SDR/run.py): Uvicorn runner for SDR service (`python -m MicroServices.SDR.run`).
- `[NEW]` [__init__.py](file:///home/lathiss/Projects/Scrape_the_Verse/MicroServices/SDR/__init__.py): SDR package export.

### 2. Lead Finder Outbound Dispatcher (`MicroServices/Lead_Finder/` / `leadfinder/`)
- `[NEW]` [lead_manager_client.py](file:///home/lathiss/Projects/Scrape_the_Verse/MicroServices/Lead_Finder/export/lead_manager_client.py): Async HTTP client for sending discovered targets to SDR (:8081) and Lead Manager (:8082).
- `[MODIFY]` [main.py](file:///home/lathiss/Projects/Scrape_the_Verse/MicroServices/Lead_Finder/main.py): Add `/api/v1/scrape/audit-and-register` endpoint connecting Lead Finder directly to SDR and Lead Manager.

### 3. Environment & Networking
- `[MODIFY]` [.env](file:///home/lathiss/Projects/Scrape_the_Verse/.env): Add `SDR_API_PORT=8081` and configure cross-service URLs.

### 4. Comprehensive Tests (`MicroServices/SDR/tests/` & Integration Suite)
- `[NEW]` [test_opportunity_builder.py](file:///home/lathiss/Projects/Scrape_the_Verse/MicroServices/SDR/tests/test_opportunity_builder.py): Unit tests for score derivation and opportunity extraction.
- `[NEW]` [test_sdr_server.py](file:///home/lathiss/Projects/Scrape_the_Verse/MicroServices/SDR/tests/test_sdr_server.py): FastAPI route tests for SDR service.
- `[NEW]` [test_e2e_lead_pipeline.py](file:///home/lathiss/Projects/Scrape_the_Verse/MicroServices/Lead_Manager/tests/test_e2e_lead_pipeline.py): End-to-end multi-service test: Lead Finder Target → SDR Crawl & Audit → Lead Manager Opportunity Ingestion & Human Review Task Creation.

---

## Verification Steps
1. Run unit tests on Opportunity Builder and SDR Server.
2. Run end-to-end integration tests linking SDR with Lead Manager.
3. Validate live HTTP endpoints on port 8081 (`/health`, `/.well-known/agent.json`).
