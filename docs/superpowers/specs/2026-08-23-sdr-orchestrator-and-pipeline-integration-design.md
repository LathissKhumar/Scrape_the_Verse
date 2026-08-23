# SDR Microservice & Lead Pipeline Integration Design Spec

**Date**: 2026-08-23  
**Status**: APPROVED  
**Target Services**: SDR Microservice (:8081), Lead Finder (:8000), Lead Manager (:8082)

---

## 1. Executive Summary

In the AgencyOS multi-agent ecosystem, a prospect is not simply a scraped business directory row. A scraped business only becomes a legitimate **Lead** once its digital footprint (website, SEO, performance, UX) has been audited and concrete **Opportunities** (Website Redesign, Local SEO, CRO, Performance) are identified.

This specification details:
1. **SDR Microservice (`:8081`)**: Wrapping LibreCrawl and the modular SEO Analyzers into an autonomous FastAPI service.
2. **Opportunity Synthesizer**: Transforming audit findings, technical metrics, and UX issues into scored `Opportunity` domain objects.
3. **Pipeline Ingestion Contract**:
   - **Lead Finder** (:8000) discovers raw company data.
   - Lead Finder delegates target URL to **SDR** (:8081).
   - **SDR** audits website, generates opportunities & proposal readiness, and registers the qualified lead in **Lead Manager** (:8082).
   - **Lead Manager** (:8082) sets stage to `OPPORTUNITY_IDENTIFIED` / `PROPOSAL_READY` and generates `REVIEW_PROPOSAL` task for human approval.

---

## 2. Architecture & Data Flow

```text
┌────────────────────────┐
│      Lead Finder       │ :8000
│  (GMaps, Bright Data,  │
│   Self-Healing Scraping│
└───────────┬────────────┘
            │
            │ 1. POST /api/v1/audit (Target Company & Website URL)
            ▼
┌────────────────────────┐
│    SDR Microservice    │ :8081
│  ┌──────────────────┐  │
│  │ LibreCrawl Engine│  │
│  └────────┬─────────┘  │
│           │            │
│  ┌────────▼─────────┐  │
│  │ 6x SEO Analyzers │  │
│  └────────┬─────────┘  │
│           │            │
│  ┌────────▼─────────┐  │
│  │Opportunity Builder  │
│  └──────────────────┘  │
└───────────┬────────────┘
            │
            │ 2. POST /api/v1/leads / A2A create_lead + opportunities
            ▼
┌────────────────────────┐
│      Lead Manager      │ :8082
│  ┌──────────────────┐  │
│  │  Policy Engine   │  │
│  └────────┬─────────┘  │
│  ┌────────▼─────────┐  │
│  │    LangGraph     │  │
│  │  State Machine   │  │
│  └────────┬─────────┘  │
│  ┌────────▼─────────┐  │
│  │   Async SQLite   │  │
│  │(Leads, Opps, Act)│  │
│  └──────────────────┘  │
└───────────┬────────────┘
            │
            │ 3. REST / SSE Timeline
            ▼
┌────────────────────────┐
│       UI / Human       │ :3000
│ (Review Proposal Task) │
└────────────────────────┘
```

---

## 3. SDR Microservice (`:8081`) Specifications

### Endpoints
- `POST /api/v1/audit`: Runs full crawl + SEO analysis + opportunity generation for a URL.
- `POST /api/v1/audit/dispatch-to-lead-manager`: Audits website and automatically posts resulting Lead + Opportunities directly to Lead Manager (`:8082`).
- `GET /.well-known/agent.json`: SDR Agent Card for A2A discovery.
- `POST /a2a/invoke`: A2A skill execution (`audit_website`, `generate_opportunities`, `create_proposal`).
- `GET /health` & `GET /ready`: Microservice status probes.

### Opportunity Generation Matrix
| Opportunity Type | Trigger Heuristic / Findings | Score Calculation |
|---|---|---|
| `WEBSITE_REDESIGN` | Mobile responsiveness errors, outdated markup, poor accessibility score, heavy non-responsive images | $100 - (\text{Design Score})$ |
| `LOCAL_SEO` | Missing Google Maps schema, NAP inconsistencies, missing local business structured data, missing sitemap | $100 - (\text{Local SEO Score})$ |
| `SPEED_PERFORMANCE` | High TTFB, large uncompressed asset sizes, poor Core Web Vitals | $100 - (\text{Performance Score})$ |
| `CONTENT_STRATEGY` | Thin content, missing meta descriptions, duplicate title tags, low word count | $100 - (\text{Content Score})$ |

---

## 4. Ingestion Contract to Lead Manager (`:8082`)

SDR delivers the payload to Lead Manager via `POST /api/v1/leads` or `POST /api/v1/events`:
```json
{
  "company_name": "Atlas Kliniek",
  "website_url": "https://atlaskliniek.nl",
  "industry": "Healthcare & Aesthetic Clinic",
  "location": "Belgium",
  "primary_contact_email": "info@atlaskliniek.nl",
  "source": "leadfinder+sdr",
  "fit_score": 85.0,
  "opportunity_score": 91.5,
  "recommended_services": ["WEBSITE_REDESIGN", "LOCAL_SEO", "SPEED_PERFORMANCE"],
  "metadata": {
    "audit_job_id": "audit_abc123",
    "pages_audited": 24,
    "issues_count": 42
  }
}
```
Followed immediately by `opportunity.created` and `proposal.created` events:
```json
{
  "type": "opportunity.created",
  "lead_id": "lead_123",
  "payload": {
    "opportunities": [
      {
        "type": "WEBSITE_REDESIGN",
        "score": 91.5,
        "problem_summary": "Non-responsive mobile viewport and poor accessibility scores on 18 subpages.",
        "evidence": [{"issue": "Missing viewport tag", "severity": "HIGH"}],
        "recommended": true
      },
      {
        "type": "LOCAL_SEO",
        "score": 86.0,
        "problem_summary": "Missing MedicalBusiness JSON-LD schema and incomplete NAP data.",
        "evidence": [{"issue": "Missing Schema.org JSON-LD", "severity": "MEDIUM"}],
        "recommended": true
      }
    ]
  }
}
```

---

## 5. Verification Requirements
1. Unit tests for Opportunity Builder.
2. Integration tests for SDR FastAPI server (`POST /api/v1/audit`).
3. End-to-end integration test: Lead Finder discovers target -> SDR audits & packages opportunities -> Lead Manager persists lead, sets stage to `OPPORTUNITY_IDENTIFIED`/`PROPOSAL_READY`, and generates human `REVIEW_PROPOSAL` task.
