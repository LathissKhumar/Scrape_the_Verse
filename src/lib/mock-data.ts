import type {
  CollectorStatus,
  SelfHealEvent,
  PipelineStage,
  BusinessIntelligence,
  MonitoringProspect,
  ResearchCollector,
} from './types'

export const PIPELINE_STAGES: PipelineStage[] = [
  {
    stage: '01',
    title: 'Lead Discovery',
    description:
      'Bright Data Scraper Studio discovers target businesses from Google Maps, Yelp, directories, and social platforms.',
    icon: '🔍',
  },
  {
    stage: '02',
    title: 'Parallel Web Research',
    description:
      'Four independent collectors run simultaneously: website quality, reviews, competitors, and social presence.',
    icon: '⚡',
  },
  {
    stage: '03',
    title: 'Self-Healing Scrapers',
    description:
      'When websites change structure, AI detects failure and generates new extraction strategies automatically.',
    icon: '🔧',
  },
  {
    stage: '04',
    title: 'Structured Intelligence',
    description:
      'Raw web data flows directly into Gemini AI as clean structured JSON — no preprocessing maze.',
    icon: '🧠',
  },
  {
    stage: '05',
    title: 'AI Sales Action',
    description:
      'Proposal, outreach, voice, and follow-up agents act on web intelligence to close opportunities.',
    icon: '🚀',
  },
]

export const ACTIVE_COLLECTORS: CollectorStatus[] = [
  {
    id: 'gmaps-discovery',
    name: 'google-maps-discovery',
    displayName: 'Google Maps Discovery',
    health: 'healthy',
    recordsToday: 12481,
    lastEvent: 'Extracted 48 new businesses',
    lastEventTime: '10:41:58',
  },
  {
    id: 'yelp-discovery',
    name: 'yelp-discovery',
    displayName: 'Yelp Discovery',
    health: 'healthy',
    recordsToday: 8249,
    lastEvent: 'Rate limit handled, resuming',
    lastEventTime: '10:42:01',
  },
  {
    id: 'competitor-sites',
    name: 'competitor-sites',
    displayName: 'Competitor Research',
    health: 'healing',
    recordsToday: 3201,
    lastEvent: 'Self-healing in progress…',
    lastEventTime: '10:42:05',
  },
  {
    id: 'review-intel',
    name: 'review-intelligence',
    displayName: 'Review Intelligence',
    health: 'healthy',
    recordsToday: 9847,
    lastEvent: 'Sentiment analysis complete',
    lastEventTime: '10:41:55',
  },
  {
    id: 'social-intel',
    name: 'social-intelligence',
    displayName: 'Social Intelligence',
    health: 'healthy',
    recordsToday: 6632,
    lastEvent: 'Instagram profiles indexed',
    lastEventTime: '10:41:59',
  },
  {
    id: 'prospect-monitor',
    name: 'prospect-monitoring',
    displayName: 'Prospect Monitoring',
    health: 'running',
    recordsToday: 1842,
    lastEvent: 'Website change detected: Urban Brew Café',
    lastEventTime: '10:42:07',
  },
]

export const SELF_HEAL_EVENTS: SelfHealEvent[] = [
  {
    time: '10:42:01',
    type: 'info',
    message: 'Collector: competitor-sites — 127 records extracted',
    collectorId: 'competitor-sites',
  },
  {
    time: '10:42:04',
    type: 'warning',
    message: '⚠ Website structure changed — selector no longer found',
    collectorId: 'competitor-sites',
  },
  {
    time: '10:42:05',
    type: 'error',
    message: '⚠ Extraction returned empty — pipeline at risk',
    collectorId: 'competitor-sites',
  },
  {
    time: '10:42:05',
    type: 'healing',
    message: 'SELF-HEALING AGENT ACTIVATED',
    collectorId: 'competitor-sites',
  },
  {
    time: '10:42:07',
    type: 'healing',
    message: 'Analyzing new page structure…',
    collectorId: 'competitor-sites',
  },
  {
    time: '10:42:09',
    type: 'healing',
    message: 'Generating repair strategy via LLM…',
    collectorId: 'competitor-sites',
  },
  {
    time: '10:42:11',
    type: 'healing',
    message: 'Testing new extraction path…',
    collectorId: 'competitor-sites',
  },
  {
    time: '10:42:13',
    type: 'success',
    message: '✓ Validation successful — schema intact',
    collectorId: 'competitor-sites',
  },
  {
    time: '10:42:14',
    type: 'success',
    message: '✓ Collector restored — 129 records extracted',
    collectorId: 'competitor-sites',
  },
]

export const DISCOVERY_SOURCES = [
  { name: 'Google Maps', records: 1248, color: '#00E5FF' },
  { name: 'Yelp', records: 824, color: '#EC0AFF' },
  { name: 'Local Directories', records: 409, color: '#6D28D9' },
]

export const BUSINESS_INTEL_EXAMPLE: BusinessIntelligence = {
  businessName: 'Urban Brew Café',
  website: null,
  rating: 4.7,
  reviews: 280,
  competitors: 12,
  websiteQuality: 0,
  leadScore: 92,
  opportunity: 'High',
  recommendation:
    'Build a modern website with online ordering and reservation functionality.',
}

export const RESEARCH_COLLECTORS: ResearchCollector[] = [
  {
    id: 'website-quality',
    title: 'Website Quality',
    metrics: [
      { label: 'Page Speed', value: 'N/A — No site' },
      { label: 'Mobile', value: 'N/A' },
      { label: 'HTTPS', value: 'N/A' },
      { label: 'Score', value: '0 / 100' },
    ],
    status: 'complete',
  },
  {
    id: 'reviews',
    title: 'Customer Reviews',
    metrics: [
      { label: 'Rating', value: '4.7 ★' },
      { label: 'Reviews', value: '280' },
      { label: 'Sentiment', value: 'Very Positive' },
      { label: 'Trend', value: '↑ Growing' },
    ],
    status: 'complete',
  },
  {
    id: 'competitors',
    title: 'Competitor Intel',
    metrics: [
      { label: 'Top Rivals', value: '12 found' },
      { label: 'Avg Rating', value: '3.9 ★' },
      { label: 'With Sites', value: '11 / 12' },
      { label: 'Gap', value: 'High' },
    ],
    status: 'complete',
  },
  {
    id: 'social',
    title: 'Social Presence',
    metrics: [
      { label: 'Instagram', value: '@urbanbrewatx' },
      { label: 'Followers', value: '2,841' },
      { label: 'Engagement', value: '6.2%' },
      { label: 'Frequency', value: '3×/week' },
    ],
    status: 'complete',
  },
]

export const MONITORING_PROSPECTS: MonitoringProspect[] = [
  {
    id: '1',
    name: 'Urban Brew Café',
    website: 'not-found',
    monitoring: true,
    socialMonitoring: true,
    competitorMonitoring: true,
  },
  {
    id: '2',
    name: 'Tex-Mex Junction',
    website: 'not-found',
    monitoring: true,
    socialMonitoring: false,
    competitorMonitoring: true,
  },
]

export const CLIENT_METRICS = {
  prospectsFound: 12842,
  qualified: 1284,
  hotOpportunities: 217,
  contacted: 342,
  responses: 87,
  meetings: 23,
  pipelineValue: '₹12.4L',
}

export const CI_COLLECTORS = [
  { name: 'Collector A — Google Maps Discovery', status: 'pass' as const },
  { name: 'Collector B — Review Intelligence', status: 'pass' as const },
  { name: 'Collector C — Competitor Research', status: 'fail' as const },
  { name: 'Collector D — Social Intelligence', status: 'pass' as const },
]
