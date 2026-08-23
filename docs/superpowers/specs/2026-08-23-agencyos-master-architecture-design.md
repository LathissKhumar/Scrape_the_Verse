# AgencyOS AI SDR Master Architecture Design Specification

**Reference**: [arct_agencyos.jpeg](file:///home/lathiss/Projects/Scrape_the_Verse/arct_agencyos.jpeg)  
**Status**: APPROVED & ALIGNED VIA /grill-me  
**Date**: 2026-08-23  

---

## 1. System Architecture & Topology

AgencyOS is an autonomous, multi-agent AI Sales Development Representative (SDR) and Agency Operating System structured as follows:

```text
                               ┌─────────────────────────────┐
                               │        DATA SOURCES         │
                               │  (GMaps, Yelp, YP, Avvo)    │
                               └──────────────┬──────────────┘
                                              │
                                              ▼
                               ┌─────────────────────────────┐
                               │   1. LEAD FINDER AGENT      │ :8000
                               │   (Self-Healing Scraping)   │
                               └──────────────┬──────────────┘
                                              │
                                              ▼
                               ┌─────────────────────────────┐
                               │   2. DATA NORMALIZATION     │ (In-Flight in SDR)
                               │ (Dedupe, Validate, Enrich)  │
                               └──────────────┬──────────────┘
                                              │
                       ┌──────────────────────┴──────────────────────┐
                       │ (Website Exists)                            │ (No Website)
                       ▼                                             ▼
        ┌─────────────────────────────┐               ┌─────────────────────────────┐
        │ 3. PARALLEL ANALYSIS LAYER  │               │ 9. CALL BOT / VOICE AGENT   │ :8084
        │ ┌─────────────────────────┐ │               │ (Pitch Website Creation &   │
        │ │ Website/SEO Audit Agent │ │               │  Local Maps Optimization)   │
        │ │ (LibreCrawl 6x Analyzers│ │               │ ┌─────────────────────────┐ │
        │ └─────────────────────────┘ │               │ │ A2A Invokable / Twilio  │ │
        │ ┌─────────────────────────┐ │               │ │ Multi-turn State Engine │ │
        │ │ Business Analysis Agent │ │               │ │ Transcript & Booking Gen│ │
        │ │ (DuckDuckGo Live Search │ │               │ └────────────┬────────────┘ │
        │ │  + Qwen3/Gemini Profile)│ │               └──────────────┼──────────────┘
        │ └─────────────────────────┘ │                              │
        └──────────────┬──────────────┘                              │
                       │                                             │
                       ▼                                             │
        ┌─────────────────────────────┐                              │
        │ 4. PROMPT GENERATION LAYER  │                              │
        │ (Sales Narrative & Angles)  │                              │
        └──────────────┬──────────────┘                              │
                       │                                             │
                       ▼                                             │
        ┌─────────────────────────────┐                              │
        │ 5. OPPORTUNITY ENGINE       │                              │
        │ (Agency Service Matching)   │                              │
        └──────────────┬──────────────┘                              │
                       │                                             │
                       ▼                                             │
        ┌─────────────────────────────┐                              │
        │ 6. PROPOSAL GENERATOR       │                              │
        │ (Markdown / PDF Deliverable)│                              │
        └──────────────┬──────────────┘                              │
                       │                                             │
                       ▼                                             │
        ┌─────────────────────────────┐                              │
        │ 7. OUTREACH PREPARATION     │                              │
        │ (Emails, Script, LinkedIn)  │                              │
        └──────────────┬──────────────┘                              │
                       │                                             │
                       ▼                                             │
        ┌─────────────────────────────┐                              │
        │ 8. LEAD MANAGEMENT CRM      │◄─────────────────────────────┘
        │ (17 Stages, Tasks, Timeline,│ :8082
        │  RFC 5545 .ics Scheduler)   │
        └──────────────┬──────────────┘
                       │
                       ▼
        ┌─────────────────────────────┐
        │ 10. SDR DASHBOARD FRONTEND  │ :3000
        │ (Command Center UI & HITL)  │
        └─────────────────────────────┘
```

---

## 2. Layer-by-Layer Detailed Specifications

### Layer 1: Lead Finder Agent (`:8000`)
- **Package**: `MicroServices/leadfinder/` & `MicroServices/Lead_Finder/`
- **Responsibilities**: Multi-directory scraper (Google Maps, YellowPages, Yelp) with Playwright, extraction pipelines, and self-healing memory.
- **Output**: Raw lead dictionaries with company name, phone, address, website URL, and directory rating.

### Layer 2: Data Normalization (In-Flight in SDR)
- **Module**: `MicroServices/SDR/normalizer.py`
- **Responsibilities**:
  - Deduplication via normalized domain / phone hash.
  - Email syntax and MX record validation.
  - Website reachability, HTTP status, and SSL certificate verification.
  - Industry auto-classification and NAP (Name, Address, Phone) standardization.

### Layer 3: Parallel Analysis Layer (`:8081`)
- **Module**: `MicroServices/SDR/analysis_orchestrator.py`
- **Execution**: Concurrent execution via `asyncio.gather`:
  1. **Website / SEO Analysis Agent**:
     - LibreCrawl deep crawl (HTML DOM, links, scripts, sitemaps).
     - 6-domain SEO Analyzers (`technical`, `onpage`, `content`, `schema`, `local`, `performance`).
     - Conversion & CTA detector (booking forms, phone click-to-call, live chat presence).
  2. **Business Analysis Agent**:
     - Uses **DuckDuckGo live web search** to extract competitor listings, customer review sentiment, and local market reputation.
     - Invokes Ollama (`qwen3:8b`) with Gemini 2.0 Flash fallback to generate business profile, competitor analysis, customer demographics, and SWOT analysis.

### Layer 4: Prompt Generation Layer
- **Module**: `MicroServices/SDR/prompt_generator.py`
- **Responsibilities**:
  - Synthesizes technical SEO audit findings + live business analysis insights.
  - Generates `PersonalizedPromptPack`:
    - `company_context`: Narrative summary of the business and digital maturity.
    - `key_problems`: Exact technical, structural, and competitive gaps.
    - `value_angles`: Tailored ROI propositions for the business owner.
    - `proof_points`: Relevant industry case studies and conversion metrics.
    - `objections_and_responses`: 4-6 specific objection counters for gatekeepers and owners.

### Layer 5: Opportunity Engine
- **Module**: `MicroServices/SDR/opportunity_engine.py`
- **Responsibilities**:
  - Evaluates prospect weaknesses against a structured **Agency Service Catalog**:
    1. `WEBSITE_REDESIGN`: Modern UX, mobile optimization, conversion architecture ($1,500–$3,500).
    2. `LOCAL_SEO`: Google 3-Pack Schema.org injection, citation audit, reviews booster ($750).
    3. `SPEED_PERFORMANCE`: Core Web Vitals optimization (<1.8s load target) ($500).
    4. `CONTENT_STRATEGY`: High-intent service landing pages and search copy ($900).
    5. `AI_BOOKING_FUNNEL`: Automated customer booking bot and CRM integration ($1,200).
  - Calculates impact score (1-100), urgency score (1-100), and expected business outcomes.

### Layer 6: Proposal Generator
- **Module**: `MicroServices/SDR/proposal_generator.py`
- **Responsibilities**:
  - Generates standard **Markdown / PDF proposal documents** for internal CRM record-keeping and lead maintenance.
  - Sections: Executive Summary, Current State Audit Breakdown, Recommended Solutions & Deliverables, Investment & Pricing Matrix, Implementation Timeline, and Next Steps.

### Layer 7: Outreach Preparation
- **Module**: `MicroServices/SDR/outreach_preparer.py`
- **Responsibilities**:
  - Generates a **Multi-Touch Omnichannel Outreach Pack**:
    1. **3-Touch Cold Email Sequence**:
       - Touch 1 (Day 1): Specific technical weakness hook + free value offer.
       - Touch 2 (Day 4): Case study / proof point showing ROI.
       - Touch 3 (Day 8): Permission to close file / soft breakup.
    2. **Dynamic Cold Call Script**:
       - Gatekeeper bypass opening.
       - Business owner 15-second value hook.
       - Branching objection counters (Already have agency, No budget, Word of mouth).
       - Call-to-action for 10-minute strategy session.
    3. **LinkedIn Connection Note & InMail Message**.
    4. **SMS / WhatsApp Follow-up Teaser**.

### Layer 8: Lead Management CRM (`:8082`)
- **Package**: `MicroServices/Lead_Manager/`
- **Responsibilities**:
  - System of Record with Async SQLite + WAL mode.
  - Deterministic 17-stage lifecycle state machine (`DISCOVERED` -> `QUALIFIED` -> `OPPORTUNITY_IDENTIFIED` -> `PROPOSAL_READY` -> `CONTACT_READY` -> `CONTACTED` -> `ENGAGED` -> `MEETING_REQUESTED` -> `MEETING_SCHEDULED` -> `NEGOTIATION` -> `WON`).
  - Task generation, timeline activity logging, RFC 5545 `.ics` meeting scheduling, and stale lead background scanner.

### Layer 9: Call Bot / Voice Agent (`:8084`)
- **Package**: `MicroServices/Voice_Agent/`
- **Responsibilities**:
  - A2A-invokable microservice running on port **8084**.
  - Engages leads with **no website** (pitching custom website creation and local maps setup) or conducts qualification calls.
  - State Engine: `OPENING` -> `PITCH` -> `FAQ_AND_OBJECTIONS` -> `MEETING_BOOKING` -> `CLOSING`.
  - Generates `call_summary`, `transcript`, `interest_score` (1-100), and auto-books meetings in Lead Manager (`:8082`).
  - Includes interactive simulation mode for automated testing and webhook adapters for Twilio / WebRTC / ElevenLabs / LiveKit.

---

## 3. Microservice Network & Port Allocation

| Microservice | Port | Primary Roles | Key Endpoints |
|---|---|---|---|
| **Lead Finder** | `8000` | Discovery, multi-directory scraper | `POST /api/v1/scrape`, `POST /api/v1/pipeline/dispatch` |
| **SDR Intelligence** | `8081` | Normalization, SEO/Business Audit, Prompt Gen, Opportunity Engine, Proposal Gen, Outreach Prep | `POST /api/v1/sdr/process`, `POST /api/v1/audit`, `/.well-known/agent.json`, `POST /a2a/invoke` |
| **Lead Manager** | `8082` | System of Record, CRM lifecycle state machine, tasks, timeline, meetings | `POST /api/v1/leads`, `POST /api/v1/events`, `GET /api/v1/timeline/stream`, `POST /api/v1/meetings`, `/.well-known/agent.json` |
| **Communication Service** | `8083` | Zero-budget IMAP/SMTP sync & Ollama intent detection | `POST /api/v1/mail/sync`, `POST /api/v1/mail/send` |
| **Voice Agent / Call Bot** | `8084` | Real-time call handling, qualification, booking | `POST /api/v1/voice/simulate-call`, `POST /api/v1/voice/webhook`, `/.well-known/agent.json`, `POST /a2a/invoke` |
| **Frontend UI** | `3000` | Unified Command Center Dashboard & HITL | Kanban pipeline, Timeline feeds, Proposal review & approval |
