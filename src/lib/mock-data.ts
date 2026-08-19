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
      'Sweeps maps, business directories, and review sites to identify targeted prospects.',
    icon: '🔍',
  },
  {
    stage: '02',
    title: 'Parallel Research',
    description:
      'Four concurrent collectors evaluate website quality, customer sentiment, competitors, and social footprint.',
    icon: '⚡',
  },
  {
    stage: '03',
    title: 'Self-Healing Engine',
    description:
      'When target site layouts change, AI agents automatically regenerate extraction rules in real time.',
    icon: '🛡️',
  },
  {
    stage: '04',
    title: 'Structured Intelligence',
    description:
      'Raw web payload normalizes into structured JSON and feeds directly into Gemini AI models.',
    icon: '🧠',
  },
  {
    stage: '05',
    title: 'Autonomous Sales Action',
    description:
      'Proposals, outreach emails, voice calls, and re-engagement triggers execute automatically.',
    icon: '🚀',
  },
]

export const ACTIVE_COLLECTORS: CollectorStatus[] = [
  {
    id: 'gmaps-discovery',
    name: 'google-maps-discovery',
    displayName: 'Google Maps Discovery',
    health: 'healthy',
    recordsToday: 184200,
    lastEvent: 'Extracted 64 new business listings',
    lastEventTime: '11:38:02',
  },
  {
    id: 'yelp-discovery',
    name: 'yelp-discovery',
    displayName: 'Directory Discovery',
    health: 'healthy',
    recordsToday: 94200,
    lastEvent: 'Rate limit handled cleanly',
    lastEventTime: '11:38:05',
  },
  {
    id: 'competitor-sites',
    name: 'competitor-sites',
    displayName: 'Competitor Intelligence',
    health: 'healing',
    recordsToday: 42100,
    lastEvent: 'Self-healing in progress…',
    lastEventTime: '11:38:12',
  },
  {
    id: 'review-intel',
    name: 'review-intelligence',
    displayName: 'Review Sentiment',
    health: 'healthy',
    recordsToday: 112800,
    lastEvent: 'Sentiment scoring complete',
    lastEventTime: '11:37:58',
  },
  {
    id: 'social-intel',
    name: 'social-intelligence',
    displayName: 'Social Footprint',
    health: 'healthy',
    recordsToday: 78400,
    lastEvent: 'Instagram & LinkedIn indexed',
    lastEventTime: '11:38:01',
  },
  {
    id: 'prospect-monitor',
    name: 'prospect-monitoring',
    displayName: 'Prospect Monitoring',
    health: 'running',
    recordsToday: 24800,
    lastEvent: 'New domain detected: urbanbrewchennai.com',
    lastEventTime: '11:38:15',
  },
]

export const SELF_HEAL_EVENTS: SelfHealEvent[] = [
  {
    time: '11:38:01',
    type: 'info',
    message: 'Collector: competitor-intelligence — 142 records extracted',
    collectorId: 'competitor-sites',
  },
  {
    time: '11:38:04',
    type: 'warning',
    message: '⚠ Target DOM layout changed — selector mismatch',
    collectorId: 'competitor-sites',
  },
  {
    time: '11:38:05',
    type: 'error',
    message: '⚠ Extraction return empty — triggering repair workflow',
    collectorId: 'competitor-sites',
  },
  {
    time: '11:38:05',
    type: 'healing',
    message: 'SELF-HEALING AGENT ACTIVATED',
    collectorId: 'competitor-sites',
  },
  {
    time: '11:38:07',
    type: 'healing',
    message: 'Analyzing DOM tree structure…',
    collectorId: 'competitor-sites',
  },
  {
    time: '11:38:09',
    type: 'healing',
    message: 'Synthesizing new extraction rules via LLM…',
    collectorId: 'competitor-sites',
  },
  {
    time: '11:38:11',
    type: 'healing',
    message: 'Testing validation payload…',
    collectorId: 'competitor-sites',
  },
  {
    time: '11:38:13',
    type: 'success',
    message: '✓ Extraction path verified — schema intact',
    collectorId: 'competitor-sites',
  },
  {
    time: '11:38:14',
    type: 'success',
    message: '✓ Collector restored — 145 records extracted',
    collectorId: 'competitor-sites',
  },
]

export const DISCOVERY_SOURCES = [
  { name: 'Google Maps', records: 1480, color: '#38BDF8' },
  { name: 'Yelp & Directories', records: 680, color: '#8B5CF6' },
  { name: 'Local Business Registries', records: 321, color: '#34D399' },
]

export const BUSINESS_INTEL_EXAMPLE: BusinessIntelligence = {
  businessName: 'Urban Brew Café',
  location: 'Chennai, India',
  website: null,
  rating: 4.7,
  reviews: 280,
  competitors: 5,
  digitalPresenceScore: 38,
  leadScore: 92,
  opportunity: 'HIGH',
  recommendation: 'Strong opportunity for a modern digital presence + online ordering.',
}

export const RESEARCH_COLLECTORS: ResearchCollector[] = [
  {
    id: 'website-quality',
    title: 'Website Quality',
    metrics: [
      { label: 'Page Speed', value: 'N/A (No Site)' },
      { label: 'Mobile Responsive', value: 'N/A' },
      { label: 'HTTPS Security', value: 'N/A' },
      { label: 'Presence Score', value: '38 / 100' },
    ],
    status: 'complete',
  },
  {
    id: 'reviews',
    title: 'Customer Reviews',
    metrics: [
      { label: 'Rating', value: '4.7 ★' },
      { label: 'Review Count', value: '280' },
      { label: 'Customer Sentiment', value: 'Very Positive' },
      { label: 'Growth Trend', value: '↑ High Intent' },
    ],
    status: 'complete',
  },
  {
    id: 'competitors',
    title: 'Competitor Intel',
    metrics: [
      { label: 'Direct Rivals', value: '5 Identified' },
      { label: 'Rival Avg Rating', value: '4.1 ★' },
      { label: 'With Active Site', value: '5 / 5' },
      { label: 'Competitive Gap', value: 'High' },
    ],
    status: 'complete',
  },
  {
    id: 'social',
    title: 'Social Footprint',
    metrics: [
      { label: 'Instagram', value: '@urbanbrewchennai' },
      { label: 'Followers', value: '4,120' },
      { label: 'Engagement Rate', value: '5.8%' },
      { label: 'Posting Frequency', value: 'Active' },
    ],
    status: 'complete',
  },
]

export const MONITORING_PROSPECTS: MonitoringProspect[] = [
  {
    id: '1',
    name: 'Urban Brew Café',
    location: 'Chennai, India',
    website: 'not-detected',
    monitoring: true,
    socialMonitoring: true,
    competitorMonitoring: true,
  },
  {
    id: '2',
    name: 'Apex Dental Care',
    location: 'Chennai, India',
    website: 'not-detected',
    monitoring: true,
    socialMonitoring: false,
    competitorMonitoring: true,
  },
]

export const CLIENT_METRICS = {
  prospectsFound: 2481,
  matchedCriteria: 217,
  highOpportunities: 87,
  contacted: 142,
  responses: 48,
  meetings: 19,
  pipelineValue: '$184,000',
}

export const CI_COLLECTORS = [
  { name: 'Collector A — Maps Discovery', status: 'pass' as const },
  { name: 'Collector B — Sentiment Intel', status: 'pass' as const },
  { name: 'Collector C — Competitor Crawler', status: 'fail' as const },
  { name: 'Collector D — Social Indexer', status: 'pass' as const },
]
