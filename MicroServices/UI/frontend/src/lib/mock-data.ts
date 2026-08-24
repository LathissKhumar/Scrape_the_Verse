import type {
  CollectorStatus,
  SelfHealEvent,
  PipelineStage,
  BusinessIntelligence,
  MonitoringProspect,
  ResearchCollector,
} from "./types";

export const PIPELINE_STAGES: PipelineStage[] = [
  {
    stage: "01",
    roleBadge: "DISCOVERY",
    title: "Lead Finder Agent",
    subtitle: "The entry point. Finds the prospects.",
    description:
      "Scrapes and discovers business listings from IndiaMART, Yelp, Google Maps, Avvo, and other directories. Extracts structured lead data — company name, location, category, website URL, contact details — and passes it downstream. It doesn't need to understand the business deeply. It just needs to find it.",
    output: "Structured business lead with source metadata",
    icon: "search",
  },
  {
    stage: "02",
    roleBadge: "NORMALIZATION",
    title: "Lead Normalizer",
    subtitle: "One schema to rule them all.",
    description:
      "IndiaMART gives you company_name and gstin. Yelp gives you rating and reviews_count. Avvo gives you avvo_rating and practice_areas. The Lead Normalizer maps every source schema into a single unified business profile so all downstream agents work the same way regardless of where the lead came from.",
    output:
      "Unified lead object: business_name, industry, location, website, contact, source",
    icon: "zap",
  },
  {
    stage: "03",
    roleBadge: "WEBSITE INTELLIGENCE",
    title: "Website & SEO Analysis Agent",
    subtitle: "The digital audit engine.",
    description:
      "Crawls the business website and runs a full technical and content audit. Finds the real problems — not just a score. Reports exactly what is broken, what is missing, and what is costing the business visibility and leads.",
    subAgents: [
      {
        name: "Crawl Agent",
        desc: "checks crawlability, indexability, redirects, robots, sitemap",
      },
      {
        name: "On-Page SEO Agent",
        desc: "audits titles, meta descriptions, H1 tags, heading structure",
      },
      {
        name: "Content Agent",
        desc: "identifies thin content, missing service pages, content gaps",
      },
      {
        name: "Local SEO Agent",
        desc: "checks local search signals and location-specific opportunities",
      },
      {
        name: "Performance Agent",
        desc: "flags performance-related findings affecting SEO",
      },
    ],
    output:
      "SEO report: score, specific page-level problems, missing pages, content gaps",
    icon: "shield-check",
  },
  {
    stage: "04",
    roleBadge: "BUSINESS INTELLIGENCE",
    title: "Business Analysis Agent",
    subtitle: "The research team. All in one agent.",
    description:
      "Understands the business from the outside in — who they are, who their customers are, what the market looks like, who their competitors are, and what they actually sell. This is the layer that turns a website audit into a business opportunity.",
    subAgents: [
      {
        name: "Business Profile Agent",
        desc: "identifies industry, business model, services, positioning, scale",
      },
      {
        name: "Market Analysis Agent",
        desc: "maps local market conditions, digital demand, search behavior",
      },
      {
        name: "Customer Analysis Agent",
        desc: "profiles customer segments, pain points, needs, decision factors",
      },
      {
        name: "Competitor Analysis Agent",
        desc: "identifies competitors, their digital presence, positioning gaps",
      },
      {
        name: "Service Analysis Agent",
        desc: "maps business services against website visibility",
      },
    ],
    output:
      "Full business context: profile, market, customers, competitors, services",
    icon: "brain-circuit",
  },
  {
    stage: "05",
    roleBadge: "OPPORTUNITY DETECTION",
    title: "Opportunity Engine",
    subtitle: "Where research becomes revenue.",
    description:
      "Takes the SEO findings and business context and asks one question: What problem exists here, and what opportunity does it represent? Every output includes a problem, the evidence behind it, the customer need it affects, and the digital service that addresses it. No hallucinations. No generic advice. Evidence-backed opportunities only.",
    subAgents: [
      {
        name: "Business Problem Agent",
        desc: "identifies problems from website and business evidence",
      },
      {
        name: "Opportunity Agent",
        desc: "maps problems to digital service opportunities",
      },
      {
        name: "Business Scoring Agent",
        desc: "scores each lead across 5 dimensions and assigns priority",
      },
    ],
    output:
      "Opportunity brief: problem + evidence + customer need + recommended service + priority score",
    icon: "zap",
  },
  {
    stage: "06",
    roleBadge: "IMPLEMENTATION",
    title: "Prompt Generation Agent",
    subtitle: "The bridge between research and execution.",
    description:
      "Takes everything the system knows about the business and generates a complete, implementation-ready website specification. Not a summary of the SEO report. Not a generic template. A structured prompt that tells an AI website builder exactly what to build, who it's for, what pages to create, what content to include, and what SEO rules to follow — built from verified business data only.",
    compatibleWith:
      "Lovable · v0 · Bolt · Firebase Studio · Claude Code · Cursor · OpenCode",
    output:
      "Website implementation prompt: architecture, pages, content, SEO, UX, conversion flow",
    icon: "rocket",
  },
  {
    stage: "07",
    roleBadge: "OUTREACH",
    title: "Outreach & Lead Management Agent",
    subtitle: "From opportunity to conversation.",
    description:
      "Uses the business context and opportunity brief to generate a personalized, evidence-backed outreach message. Not a cold template — a pitch built from what the agent actually found. Then tracks every lead through the pipeline: contacted, interested, proposal sent, meeting booked, won or lost.",
    output:
      "Personalized outreach draft + lead status tracking + follow-up queue",
    icon: "search",
  },
];

export const ACTIVE_COLLECTORS: CollectorStatus[] = [
  {
    id: "gmaps-discovery",
    name: "google-maps-discovery",
    displayName: "Google Maps Discovery",
    health: "healthy",
    recordsToday: 184200,
    lastEvent: "Extracted 64 new business listings",
    lastEventTime: "11:38:02",
  },
  {
    id: "yelp-discovery",
    name: "yelp-discovery",
    displayName: "Directory Discovery",
    health: "healthy",
    recordsToday: 94200,
    lastEvent: "Rate limit handled cleanly",
    lastEventTime: "11:38:05",
  },
  {
    id: "competitor-sites",
    name: "competitor-sites",
    displayName: "Competitor Intelligence",
    health: "healing",
    recordsToday: 42100,
    lastEvent: "Self-healing in progress…",
    lastEventTime: "11:38:12",
  },
  {
    id: "review-intel",
    name: "review-intelligence",
    displayName: "Review Sentiment",
    health: "healthy",
    recordsToday: 112800,
    lastEvent: "Sentiment scoring complete",
    lastEventTime: "11:37:58",
  },
  {
    id: "social-intel",
    name: "social-intelligence",
    displayName: "Social Footprint",
    health: "healthy",
    recordsToday: 78400,
    lastEvent: "Instagram & LinkedIn indexed",
    lastEventTime: "11:38:01",
  },
  {
    id: "prospect-monitor",
    name: "prospect-monitoring",
    displayName: "Prospect Monitoring",
    health: "running",
    recordsToday: 24800,
    lastEvent: "New domain detected: urbanbrewchennai.com",
    lastEventTime: "11:38:15",
  },
];

export const SELF_HEAL_EVENTS: SelfHealEvent[] = [
  {
    time: "11:38:01",
    type: "info",
    message: "Collector: competitor-intelligence — 142 records extracted",
    collectorId: "competitor-sites",
  },
  {
    time: "11:38:04",
    type: "warning",
    message: "Target DOM layout changed — selector mismatch",
    collectorId: "competitor-sites",
  },
  {
    time: "11:38:05",
    type: "error",
    message: "Extraction return empty — triggering repair workflow",
    collectorId: "competitor-sites",
  },
  {
    time: "11:38:05",
    type: "healing",
    message: "SELF-HEALING AGENT ACTIVATED",
    collectorId: "competitor-sites",
  },
  {
    time: "11:38:07",
    type: "healing",
    message: "Analyzing DOM tree structure…",
    collectorId: "competitor-sites",
  },
  {
    time: "11:38:09",
    type: "healing",
    message: "Synthesizing new extraction rules via LLM…",
    collectorId: "competitor-sites",
  },
  {
    time: "11:38:11",
    type: "healing",
    message: "Testing validation payload…",
    collectorId: "competitor-sites",
  },
  {
    time: "11:38:13",
    type: "success",
    message: "Extraction path verified — schema intact",
    collectorId: "competitor-sites",
  },
  {
    time: "11:38:14",
    type: "success",
    message: "Collector restored — 145 records extracted",
    collectorId: "competitor-sites",
  },
];

export const DISCOVERY_SOURCES = [
  { name: "Google Maps", records: 1480, color: "#38BDF8" },
  { name: "Yelp & Directories", records: 680, color: "#8B5CF6" },
  { name: "Local Business Registries", records: 321, color: "#34D399" },
];

export const BUSINESS_INTEL_EXAMPLE: BusinessIntelligence = {
  businessName: "Urban Brew Café",
  location: "Chennai, India",
  website: null,
  rating: 4.7,
  reviews: 280,
  competitors: 5,
  digitalPresenceScore: 38,
  leadScore: 92,
  opportunity: "HIGH",
  recommendation:
    "Strong opportunity for a modern digital presence + online ordering.",
};

export const RESEARCH_COLLECTORS: ResearchCollector[] = [
  {
    id: "website-quality",
    title: "Website Quality",
    metrics: [
      { label: "Page Speed", value: "N/A (No Site)" },
      { label: "Mobile Responsive", value: "N/A" },
      { label: "HTTPS Security", value: "N/A" },
      { label: "Presence Score", value: "38 / 100" },
    ],
    status: "complete",
  },
  {
    id: "reviews",
    title: "Customer Reviews",
    metrics: [
      { label: "Rating", value: "4.7" },
      { label: "Review Count", value: "280" },
      { label: "Customer Sentiment", value: "Very Positive" },
      { label: "Growth Trend", value: "High Intent" },
    ],
    status: "complete",
  },
  {
    id: "competitors",
    title: "Competitor Intel",
    metrics: [
      { label: "Direct Rivals", value: "5 Identified" },
      { label: "Rival Avg Rating", value: "4.1" },
      { label: "With Active Site", value: "5 / 5" },
      { label: "Competitive Gap", value: "High" },
    ],
    status: "complete",
  },
  {
    id: "social",
    title: "Social Footprint",
    metrics: [
      { label: "Instagram", value: "@urbanbrewchennai" },
      { label: "Followers", value: "4,120" },
      { label: "Engagement Rate", value: "5.8%" },
      { label: "Posting Frequency", value: "Active" },
    ],
    status: "complete",
  },
];

export const AI_AGENTS = [
  {
    id: "landing-page",
    name: "Landing Page Agent",
    agentRole: "Automated Micro-site Builder",
    icon: "file-text",
    outputTitle: "Tailored Mobile Micro-Site",
    outputSnippet: `Headline: "Fresh Coffee & Online Ordering for Urban Brew Café"\nFeatures: Mobile Menu · Instant WhatsApp Booking · Google Maps Route Integration`,
  },
  {
    id: "email-outreach",
    name: "Email Outreach Agent",
    agentRole: "Hyper-Personalized Sales Copywriter",
    icon: "mail",
    outputTitle: "Personalized Executive Email",
    outputSnippet: `Subject: "Quick thought on Urban Brew Café's digital presence"\nBody: "Hi Urban Brew Team, noticed your 4.7★ rating with 280 reviews on Maps..."`,
  },
  {
    id: "voice-script",
    name: "Voice Script Agent",
    agentRole: "AI Phone Pitch Generator",
    icon: "mic",
    outputTitle: "AI Voice Call Briefing",
    outputSnippet: `Opening: "Hello! Calling regarding Urban Brew Café's online reservation system setup..."`,
  },
];

export const MONITORING_PROSPECTS: MonitoringProspect[] = [
  {
    id: "1",
    name: "Urban Brew Café",
    location: "Chennai, India",
    website: "not-detected",
    monitoring: true,
    socialMonitoring: true,
    competitorMonitoring: true,
  },
  {
    id: "2",
    name: "Apex Dental Care",
    location: "Chennai, India",
    website: "not-detected",
    monitoring: true,
    socialMonitoring: false,
    competitorMonitoring: true,
  },
];

export const CLIENT_METRICS = {
  prospectsFound: 2481,
  matchedCriteria: 217,
  highOpportunities: 87,
  contacted: 142,
  responses: 48,
  meetings: 19,
  pipelineValue: "$184,000",
};

export const CI_COLLECTORS = [
  { name: "Collector A — Maps Discovery", status: "pass" as const },
  { name: "Collector B — Sentiment Intel", status: "pass" as const },
  { name: "Collector C — Competitor Crawler", status: "fail" as const },
  { name: "Collector D — Social Indexer", status: "pass" as const },
];
