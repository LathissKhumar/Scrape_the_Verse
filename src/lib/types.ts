export type CollectorHealth = 'healthy' | 'running' | 'healing' | 'failed'

export interface CollectorStatus {
  id: string
  name: string
  displayName: string
  health: CollectorHealth
  recordsToday: number
  lastEvent?: string
  lastEventTime?: string
}

export interface Lead {
  id: string
  name: string
  location: string
  phone?: string
  website?: string
  rating: number
  reviewCount: number
  digitalPresenceScore: number
  websiteQuality: number
  socialPresence: boolean
  competitorCount: number
  leadScore: number
  opportunity: 'High' | 'Medium' | 'Low'
  aiRecommendation: string
  source: string
}

export interface SelfHealEvent {
  time: string
  type: 'info' | 'warning' | 'success' | 'error' | 'healing'
  message: string
  collectorId?: string
}

export interface PipelineStage {
  stage: string
  title: string
  description: string
  icon: string
}

export interface BusinessIntelligence {
  businessName: string
  website: string | null
  rating: number
  reviews: number
  competitors: number
  websiteQuality: number
  leadScore: number
  opportunity: 'High' | 'Medium' | 'Low'
  recommendation: string
}

export interface MonitoringProspect {
  id: string
  name: string
  website: 'found' | 'not-found'
  monitoring: boolean
  socialMonitoring: boolean
  competitorMonitoring: boolean
  lastChange?: string
  changeType?: string
}

export interface ResearchCollector {
  id: string
  title: string
  metrics: { label: string; value: string }[]
  status: 'scraping' | 'complete' | 'idle'
}

export interface WebNode {
  x: number
  y: number
  label?: string
  color?: string
  radius?: number
}

export interface WebEdge {
  from: number
  to: number
  color?: string
  animated?: boolean
}
