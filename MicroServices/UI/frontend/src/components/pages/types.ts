export type DashboardTab =
  | "overview"
  | "discovery"
  | "analysis"
  | "proposals"
  | "outreach"
  | "calls"
  | "pipeline"
  | "scrapers";

export type PipelineStage =
  | "discovered"
  | "analyzed"
  | "proposal_ready"
  | "outreach_active"
  | "call_booked"
  | "negotiation"
  | "won"
  | "nurture";

export type DealStage = PipelineStage;

export type DecisionPath =
  "website_analysis" | "voice_bot_pitch" | "direct_outreach";

export interface LeadRecord {
  id: string;
  business_name: string;
  category: string;
  location: string;
  phone_number: string;
  website?: string;
  rating?: number;
  reviews_count?: number;
  source: "Google Maps" | "IndiaMART" | "Yelp" | "Avvo" | "Justdial" | "Custom";
  decision_path: DecisionPath;
  stage: PipelineStage;
  lead_quality_score: number; // 0 - 100
  seo_score?: number; // 0 - 100
  business_score?: number; // 0 - 100
  opportunity_priority: "High" | "Medium" | "Low";
  estimated_deal_value: number;
  contact_person?: string;
  email?: string;
  last_activity: string;
  created_at: string;
}

export interface SEOMetric {
  category: string;
  score: number;
  status: "good" | "warning" | "critical";
  details: string;
}

export interface BusinessAnalysis {
  lead_id: string;
  strengths: string[];
  weaknesses: string[];
  opportunities: string[];
  threats: string[];
  competitors: { name: string; advantage: string }[];
  recommended_offer: string;
  expected_outcomes: string;
  estimated_impact_score: number;
}

export interface Proposal {
  id: string;
  lead_id: string;
  title: string;
  executive_summary: string;
  identified_problems: string[];
  proposed_solution: string;
  deliverables: { title: string; timeline: string; price: number }[];
  total_investment: number;
  roi_estimate: string;
  status: "draft" | "ready" | "sent" | "accepted";
  created_at: string;
}

export interface OutreachAsset {
  id: string;
  lead_id: string;
  channel: "email" | "linkedin" | "call_script";
  subject?: string;
  content: string;
  sequence_step: number;
  status: "ready" | "sent" | "opened" | "replied";
}

export interface CallLog {
  id: string;
  lead_id: string;
  business_name: string;
  contact_name: string;
  phone_number: string;
  duration_seconds: number;
  status: "completed" | "in_progress" | "scheduled" | "failed";
  interest_score: number; // 0 - 100
  meeting_booked: boolean;
  meeting_time?: string;
  summary: string;
  transcript: {
    speaker: "AI SDR Agent" | "Prospect";
    text: string;
    timestamp: string;
  }[];
  audio_url?: string;
  objections: string[];
}

export interface ScraperStatusRecord {
  id: string;
  collector_id: string;
  name: string;
  target_domain: string;
  status: "READY" | "CREATING" | "HEALING" | "ERROR";
  records_extracted: number;
  health_score: number; // 0.0 - 1.0
  last_healed?: string;
  healing_attempts: number;
}
