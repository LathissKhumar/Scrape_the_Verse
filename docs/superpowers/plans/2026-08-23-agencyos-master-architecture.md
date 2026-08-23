# AgencyOS Master Implementation Plan

**Spec Reference**: `docs/superpowers/specs/2026-08-23-agencyos-master-architecture-design.md`  
**Architecture Diagram**: [arct_agencyos.jpeg](file:///home/lathiss/Projects/Scrape_the_Verse/arct_agencyos.jpeg)  

---

## 1. Execution Tasks by Layer

### Task 1: In-Flight Data Normalizer (Layer 2)
- [ ] Create `MicroServices/SDR/normalizer.py`:
  - Deduplication key generator (domain/phone hash).
  - Email syntax + MX record check.
  - Website reachability, HTTP status code, and SSL certificate validator.
  - Industry auto-classifier based on business name and keywords.

### Task 2: Parallel Analysis Layer with Live DuckDuckGo Search (Layer 3)
- [ ] Create `MicroServices/SDR/search_client.py`: DuckDuckGo search client to fetch live competitor info, customer reviews, and local reputation.
- [ ] Create `MicroServices/SDR/business_analyzer.py`: Invokes LLM (`qwen3:8b` via Ollama + Gemini fallback) with search context to generate deep Business Profile, Competitor Analysis, Customer Demographics, Strengths, Weaknesses, and Opportunities.
- [ ] Create `MicroServices/SDR/cta_detector.py`: Scans crawled HTML for conversion signals (booking forms, click-to-call, live chat widgets, lead magnets).
- [ ] Update `MicroServices/SDR/analysis_orchestrator.py`: Runs Website/SEO Agent (LibreCrawl + 6 analyzers + CTA detector) and Business Analysis Agent concurrently via `asyncio.gather`.

### Task 3: Prompt Generation Layer & Dynamic Opportunity Engine (Layers 4 & 5)
- [ ] Update `MicroServices/SDR/prompt_generator.py`: LLM-powered synthesis of Website + Business findings into `PersonalizedPromptPack`.
- [ ] Create `MicroServices/SDR/opportunity_engine.py`: Dynamic Agency Service Catalog matching (`WEBSITE_REDESIGN`, `LOCAL_SEO`, `SPEED_PERFORMANCE`, `CONTENT_STRATEGY`, `AI_BOOKING_FUNNEL`) with impact (1-100), urgency (1-100), and expected ROI outcome calculation.

### Task 4: Markdown/PDF Proposal Generator & Omnichannel Outreach Preparer (Layers 6 & 7)
- [ ] Update `MicroServices/SDR/proposal_generator.py`: Generates complete Markdown & HTML proposals for internal CRM maintenance (Executive Summary, Current State Audit, Deliverables, Pricing Matrix, Timeline, Next Steps).
- [ ] Update `MicroServices/SDR/outreach_preparer.py`: Generates Omnichannel Outreach Pack (3-step email cadence, dynamic branching cold call script with objection counters, LinkedIn connection note & message, SMS/WhatsApp teaser).

### Task 5: Voice Agent Microservice (Layer 9 - Port 8084)
- [ ] Create `MicroServices/Voice_Agent/` package:
  - `MicroServices/Voice_Agent/domain/call_session.py`: Call state models (`CallSession`, `CallTurn`, `CallStatus`, `CallDisposition`).
  - `MicroServices/Voice_Agent/state_machine.py`: Multi-turn conversational flow (`OPENING` -> `PITCH` -> `FAQ_AND_OBJECTIONS` -> `MEETING_BOOKING` -> `CLOSING`).
  - `MicroServices/Voice_Agent/telephony_adapter.py`: Webhook adapter interface for Twilio / WebRTC / ElevenLabs / LiveKit + Interactive Simulation Engine for automated testing.
  - `MicroServices/Voice_Agent/server.py`: FastAPI service on port **8084** (`POST /api/v1/voice/simulate-call`, `POST /api/v1/voice/webhook`, `GET /.well-known/agent.json`, `POST /a2a/invoke`).
  - `MicroServices/Voice_Agent/run.py`: Runner for Voice Agent service.

### Task 6: Master SDR Orchestrator & Server Updates (:8081)
- [ ] Update `MicroServices/SDR/orchestrator.py`: Connects Normalization -> Parallel Analysis -> Prompt Gen -> Opportunity Engine -> Proposal Gen -> Outreach Prep -> Lead Manager (:8082) & Voice Agent (:8084 fallback).
- [ ] Update `MicroServices/SDR/server.py`: Expose master endpoints `POST /api/v1/sdr/process`, `POST /api/v1/audit`, and A2A Agent Card.

### Task 7: Comprehensive Multi-Service Testing & Verification
- [ ] Add unit tests for `normalizer.py`, `search_client.py`, `business_analyzer.py`, `opportunity_engine.py`, and `Voice_Agent`.
- [ ] Run full end-to-end integration test: Lead Finder target -> SDR Normalization & Parallel Audit -> Opportunity & Proposal -> Outreach Pack -> Lead Manager CRM -> Voice qualification simulation -> Meeting booking.
