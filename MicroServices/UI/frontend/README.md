# 🌌 Scrape-the-Verse — Enterprise Frontend & Dashboard

A modern, high-performance web application and enterprise AI operating console built with **Next.js 16 App Router**, **React 19**, **TypeScript**, **Tailwind CSS v4**, and **Framer Motion**. Designed with a true **Apple visionOS / Liquid Glass** aesthetic, frosted glass panels (`backdrop-blur-3xl`), interactive spatial neural-web canvas animations, and seamless multi-microservice backend integrations.

---

## 📑 Table of Contents

- [🌌 Scrape-the-Verse — Enterprise Frontend \& Dashboard](#-scrape-the-verse--enterprise-frontend--dashboard)
  - [📑 Table of Contents](#-table-of-contents)
  - [✨ Key Features \& Visual Direction](#-key-features--visual-direction)
  - [🏛️ Application Architecture \& Page Structure](#️-application-architecture--page-structure)
    - [1. Public Landing Page (`/`)](#1-public-landing-page-)
    - [2. Enterprise AI Operating Console (`/dashboard`)](#2-enterprise-ai-operating-console-dashboard)
  - [🔌 Backend Microservices Integration Matrix](#-backend-microservices-integration-matrix)
    - [Microservice Endpoints Breakdown](#microservice-endpoints-breakdown)
      - [1. `leadfinder` Microservice (Port 8000)](#1-leadfinder-microservice-port-8000)
      - [2. `SDR` Microservice (Port 8081)](#2-sdr-microservice-port-8081)
      - [3. `Lead_Manager` Microservice (Port 8082)](#3-lead_manager-microservice-port-8082)
      - [4. `Voice_Agent` Microservice (Port 8084)](#4-voice_agent-microservice-port-8084)
  - [📁 Frontend Directory Structure](#-frontend-directory-structure)
  - [⚙️ Environment Configuration](#️-environment-configuration)
  - [🚀 Getting Started](#-getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [Development Server](#development-server)
    - [Production Build \& Verification](#production-build--verification)
  - [🔒 State Machine \& Real-Time Streaming](#-state-machine--real-time-streaming)

---

## ✨ Key Features & Visual Direction

- **Apple visionOS / Liquid Glass Aesthetic**: Translucent frosted panels (`backdrop-blur-3xl`, `bg-white/[0.05]`), thin luminous 1px specular borders (`border-white/[0.14]`), inner depth highlights, and clean typography.
- **Atmospheric Spatial Canvas (`NeuralWebBackground.tsx`)**: High-performance HTML5 Canvas with multi-depth 3-layer floating spatial nodes, distance-faded connecting webs, traveling data pulses, and tab-visibility auto-pause.
- **Lagging Magnetic Cursor & Particle Transitions (`ParticleDisintegrationTransition.tsx`)**: Custom magnetic interactive cursor with 3D mesh particle collapse animations transitioning seamlessly into the dashboard.
- **Fixed Static Multi-Hub Navigation**: Fixed top header with real-time breadcrumbs, active hub badges, integrated quick search, and a vertically proportioned 8-hub sidebar with smooth hover expansion.
- **Live Real-Time SSE Stream**: Native browser Server-Sent Events (SSE) listener (`useTimelineStream.ts`) streaming live lifecycle state transitions and toast notifications.
- **Resilient Fallback Mode**: Graceful fallback to rich offline mock data if backend microservices are offline or undergoing maintenance.

---

## 🏛️ Application Architecture & Page Structure

### 1. Public Landing Page (`/`)
*Entry Point:* `src/app/page.tsx`  
A high-converting marketing showcase featuring:
- **Hero Section (`Hero.tsx`)**: Horizontal dynamic text scramble effect, interactive collapsing canvas particles, and cold-tech developer workspace visualizer.
- **Pinned Horizontal Pillars (`PinnedHorizontalPillars.tsx`)**: GSAP ScrollTrigger-driven horizontal pinning showcasing the 4 core pillars of intelligent scraping.
- **Live Web Database Console (`WebDatabase.tsx`)**: Interactive query console with realistic DOM tree inspection and simulated data stream.
- **Pipeline Architecture Stream (`Pipeline.tsx`)**: Continuous upward pipeline flow depicting end-to-end data extraction and AI enrichment.
- **3D Staggered Grid Reveal (`StaggeredGridReveal.tsx`)**: 3x3 interactive card grid with 3D tilt and specular hover reflections.
- **Adaptive Vision Engine (`ImageDistortionSection.tsx`)**: Scroll-driven morphing clip-paths (circle → star polygon → rounded inset) illustrating visual DOM synthesis.
- **Self-Healing CI & Scraper Demo (`SelfHealingDemo.tsx`, `SelfHealingCI.tsx`)**: Live interactive selector mutation and AI auto-repair demonstration.
- **Sales Automation Hub (`SalesAutomation.tsx`)**: Visual breakdown of automated outreach sequences and CRM integrations.
- **System Monitoring & Kinetic Typography (`Monitoring.tsx`, `WhyScrapeVerse.tsx`)**: Animated SVG progress rings and word-by-word kinetic manifesto.

### 2. Enterprise AI Operating Console (`/dashboard`)
*Entry Point:* `src/app/dashboard/page.tsx` → `DashboardShell.tsx`  
Unified operating system containing 8 core AI hubs:

| Hub ID | Name | Component | Core Responsibilities |
|---|---|---|---|
| `overview` | **Command Center** | `DashboardOverview.tsx` | Executive swarm cockpit, stage pipeline conversion velocity, real-time live event feed, and quick action launcher. |
| `discovery` | **Lead Discovery** | `LeadDiscoveryPage.tsx` | Dual-engine discovery (Google Maps local business harvester + Bright Data B2B corporate lead extraction) with CSV export. |
| `analysis` | **360° AI Audit** | `LeadAnalysisPage.tsx` | Live headless crawler (LibreCrawl) running 6-domain audits (Technical, On-Page, Mobile, Speed, Security, Backlinks) + automated SWOT matrix. |
| `proposals` | **Proposal Studio** | `ProposalStudioPage.tsx` | Automated opportunity synthesis, 3-tier value package generator, ROI calculator, and human-in-the-loop proposal approval. |
| `outreach` | **Outreach Hub** | `OutreachHubPage.tsx` | Omnichannel campaign sequencer (AI Email drips, LinkedIn InMails, Phone scripts) with state machine transitions. |
| `calls` | **Voice Agent** | `VoiceAgentPage.tsx` | Live Twilio carrier PSTN outbound dialing, 1-line verified audio tester, and multi-turn in-browser conversational phone simulator. |
| `pipeline` | **Pipeline CRM** | `PipelinePage.tsx` | 17-stage Kanban board with drag-and-drop deal moves, and on-demand Twenty CRM Docker container spin-up/spin-down controls. |
| `scrapers` | **DCA Operations** | `ScraperStudioPage.tsx` | Self-healing Bright Data DCA collector fleet registry with 1-click healing triggers. |

---

## 🔌 Backend Microservices Integration Matrix

The frontend communicates with 4 standalone backend microservices via the typed API client located in `src/lib/api/`:

```
┌────────────────────────────────────────────────────────┐
│               Frontend (Next.js 16 :3000)              │
└───────┬──────────────┬──────────────┬───────────┬──────┘
        │              │              │           │
        ▼ :8000        ▼ :8081        ▼ :8082     ▼ :8084
 ┌─────────────┐┌─────────────┐┌─────────────┐┌─────────────┐
 │ leadfinder  ││     SDR     ││Lead_Manager ││ Voice_Agent │
 └─────────────┘└─────────────┘└─────────────┘└─────────────┘
```

### Microservice Endpoints Breakdown

#### 1. `leadfinder` Microservice (Port 8000)
*Client:* `src/lib/api/leadfinder.ts`
- `GET /health`: Health status probe for swarm telemetry.
- `POST /api/v1/gmaps/leads`: Google Maps local business harvesting engine.
- `POST /api/v1/brightdata/leads`: Bright Data B2B company and contact discovery.
- `GET /scrapers`: Registry listing all active Bright Data DCA collectors.
- `POST /scrapers/heal`: Triggers self-healing LLM selector repair for broken collectors.
- `POST /api/v1/jobs`: Async scraping batch job submitter (*Client-ready*).
- `GET /api/v1/jobs/{job_id}`: Async scraping batch job status checker (*Client-ready*).

#### 2. `SDR` Microservice (Port 8081)
*Client:* `src/lib/api/sdr.ts`
- `GET /health`: Health status probe for SDR service.
- `POST /api/v1/audit`: Executes 6-domain SEO crawl and audit via headless LibreCrawl engine.
- `POST /api/v1/pipeline/process-target`: End-to-end multi-agent pipeline (Normalization → Crawl → SWOT → Proposal → Outreach → Lead Manager auto-registration).
- `/.well-known/agent.json`, `POST /a2a/invoke`: Swarm inter-agent protocol (A2A).

#### 3. `Lead_Manager` Microservice (Port 8082)
*Client:* `src/lib/api/leadManager.ts`
- `GET /health`: Health status probe for Lead Manager service.
- `GET /api/v1/leads`: Retrieves filtered and paginated leads database.
- `POST /api/v1/leads`: Creates a new lead record from discovery or audits.
- `PATCH /api/v1/leads/{lead_id}`: Updates lead pipeline stage and fields during Kanban drag-and-drop.
- `POST /api/v1/events`: Ingests 17-stage deterministic lifecycle state transitions.
- `GET /api/v1/leads/{lead_id}/opportunities`: Fetches AI-synthesized commercial opportunities.
- `POST /api/v1/leads/{lead_id}/approve-proposal`: Triggers human-in-the-loop proposal sign-off.
- `GET /api/v1/timeline/stream` (SSE): Server-Sent Events stream for live real-time notifications.
- `GET /api/v1/crm/status`: Inspects Docker container state of Twenty CRM.
- `POST /api/v1/crm/spin-up`: Launches Twenty CRM Docker Compose services on demand.
- `POST /api/v1/crm/spin-down`: Puts Twenty CRM Docker Compose containers into sleep mode.
- `POST /api/v1/meetings`: Schedules calendar meetings (*Client-ready*).
- `PATCH /api/v1/tasks/{task_id}`: Updates task completion status (*Client-ready*).

#### 4. `Voice_Agent` Microservice (Port 8084)
*Client:* `src/lib/api/voiceAgent.ts`
- `GET /health`: Health status probe for Voice Agent telephony.
- `GET /api/v1/voice/config`: Fetches Twilio carrier phone number and carrier configuration status.
- `POST /api/v1/voice/call/initiate`: Triggers real outbound PSTN phone call via Twilio carrier.
- `POST /api/v1/voice/call/test`: Sends a 1-line verified audio delivery test call.
- `POST /api/v1/voice/simulate-call`: Runs simulated multi-turn phone conversation in the browser.
- `/api/v1/voice/twiml`, `/voice/turn`, `/voice/status-callback`, `/voice/stream` (WS): Telephony carrier webhooks & raw audio WebSocket (called by Twilio's cloud servers).

---

## 📁 Frontend Directory Structure

```
MicroServices/UI/frontend/
├── src/
│   ├── app/
│   │   ├── globals.css              # Apple visionOS CSS design tokens & utilities
│   │   ├── layout.tsx               # Root layout & font definitions
│   │   ├── page.tsx                 # Full-screen public landing page
│   │   └── dashboard/
│   │       └── page.tsx             # Main dashboard route
│   ├── components/
│   │   ├── pages/                   # 8 Enterprise AI Hubs & Shell
│   │   │   ├── DashboardShell.tsx   # Static header, sidebar, SSE toasts & notifications
│   │   │   ├── DashboardOverview.tsx# Command Center cockpit
│   │   │   ├── LeadDiscoveryPage.tsx# Google Maps & Bright Data harvester
│   │   │   ├── LeadAnalysisPage.tsx # 360° AI Website Audit & SWOT
│   │   │   ├── ProposalStudioPage.tsx# Proposal structuring & pricing
│   │   │   ├── OutreachHubPage.tsx  # Omnichannel sequences & campaigns
│   │   │   ├── VoiceAgentPage.tsx   # Twilio outbound & simulated telephony
│   │   │   ├── PipelinePage.tsx     # 17-stage Kanban & Twenty CRM Docker bridge
│   │   │   ├── ScraperStudioPage.tsx# DCA fleet registry & self-healing
│   │   │   ├── types.ts             # TypeScript interfaces for leads & stages
│   │   │   └── mockData.ts          # Resilient demo fallbacks
│   │   ├── sections/                # Landing page interactive sections
│   │   │   ├── Navbar.tsx           # Full-width frosted glass header
│   │   │   ├── Hero.tsx             # Text scramble & collapsing canvas particles
│   │   │   ├── PinnedHorizontalPillars.tsx # Horizontal scroll pinned cards
│   │   │   ├── WebDatabase.tsx      # Interactive query console
│   │   │   ├── Pipeline.tsx         # Upward streaming pipeline visualizer
│   │   │   ├── ImageDistortionSection.tsx # Scroll clip-path morphing showcase
│   │   │   ├── SelfHealingDemo.tsx  # Interactive selector repair demo
│   │   │   ├── SalesAutomation.tsx  # Omnichannel outreach visualizer
│   │   │   └── Footer.tsx           # Clean bottom footer
│   │   ├── ui/                      # Reusable visionOS components
│   │   │   ├── NeuralWebBackground.tsx # Multi-depth spatial Canvas network
│   │   │   ├── ParticleDisintegrationTransition.tsx # Magnetic cursor & mesh transition
│   │   │   ├── CustomCursor.tsx     # Lagging magnetic cursor
│   │   │   ├── Button.tsx           # Apple frosted glass & solid white CTA buttons
│   │   │   └── GradientText.tsx     # Curated HSL text gradients
│   │   └── providers/
│   │       └── SmoothScrollProvider.tsx # Lenis smooth scrolling engine
│   ├── hooks/
│   │   └── useTimelineStream.ts     # Native SSE live event stream hook
│   └── lib/
│       └── api/                     # Microservice API integration layer
│           ├── client.ts            # Base fetcher, health probing & port mapping
│           ├── leadfinder.ts        # leadfinder (:8000) client
│           ├── sdr.ts               # SDR (:8081) client
│           ├── leadManager.ts       # Lead Manager (:8082) client
│           └── voiceAgent.ts        # Voice Agent (:8084) client
├── public/                          # Static assets and images
├── package.json                     # Dependencies and scripts
├── tsconfig.json                    # TypeScript compiler options
└── next.config.ts                   # Next.js build configuration
```

---

## ⚙️ Environment Configuration

Create a `.env.local` file in `MicroServices/UI/frontend/` to customize microservice connection URLs (defaults point to standard localhost ports):

```env
# Microservice Connection Gateway Ports
NEXT_PUBLIC_GATEWAY_URL=http://localhost:8080
NEXT_PUBLIC_LEADFINDER_URL=http://localhost:8000
NEXT_PUBLIC_SDR_URL=http://localhost:8081
NEXT_PUBLIC_LEAD_MANAGER_URL=http://localhost:8082
NEXT_PUBLIC_VOICE_AGENT_URL=http://localhost:8084
```

---

## 🚀 Getting Started

### Prerequisites
- **Node.js**: v18.18.0 or higher (v20+ recommended)
- **Package Manager**: `npm`, `yarn`, or `pnpm`

### Installation
```bash
# Navigate to the frontend directory
cd MicroServices/UI/frontend

# Install dependencies
npm install
```

### Development Server
```bash
# Start Next.js development server
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser to view the application.

### Production Build & Verification
```bash
# Compile and validate TypeScript types
npm run build

# Start production server
npm run start
```

---

## 🔒 State Machine & Real-Time Streaming

The application supports the full **17-Stage Deterministic Lifecycle** governed by `Lead_Manager`:

`DISCOVERED` → `ENRICHED` → `AUDIT_QUEUED` → `AUDIT_RUNNING` → `AUDIT_COMPLETE` → `OPPORTUNITY_IDENTIFIED` → `PROPOSAL_GENERATED` → `PROPOSAL_APPROVED` → `OUTREACH_QUEUED` → `EMAIL_SENT` → `CALL_SCHEDULED` → `CALL_COMPLETED` → `MEETING_BOOKED` → `DEAL_WON` / `DEAL_LOST` / `NURTURE`

All state transitions emit live events consumed in real-time by the frontend via **Server-Sent Events (`/api/v1/timeline/stream`)**, powering instant toast updates and the notification drawer.
