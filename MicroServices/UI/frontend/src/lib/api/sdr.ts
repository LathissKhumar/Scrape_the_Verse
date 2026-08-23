/**
 * SDR Microservice API Client (Port 8081).
 * Handles Autonomous Web Crawling (LibreCrawl), 6-domain SEO Audits, Opportunity Synthesis, Proposal Generation, and Outreach Preparation.
 */

import { API_URLS, safeFetch } from './client';

export interface WebsiteAuditResult {
  url: string;
  crawl_stats?: {
    pages_crawled: number;
    depth: number;
    duration_seconds: number;
  };
  seo_score: number;
  domain_scores: {
    technical: number;
    on_page: number;
    mobile: number;
    speed: number;
    security: number;
    backlinks: number;
  };
  issues: {
    domain: string;
    severity: 'critical' | 'warning' | 'info';
    message: string;
    affected_urls?: string[];
  }[];
  swot?: {
    strengths: string[];
    weaknesses: string[];
    opportunities: string[];
    threats: string[];
  };
}

export interface SDRFullPipelineResult {
  lead_id: string;
  company_name: string;
  website_url?: string;
  status: 'PROCESSED' | 'FAILED';
  fit_score: number;
  opportunity_score: number;
  audit_summary?: WebsiteAuditResult;
  synthesized_opportunities: {
    type: string;
    score: number;
    summary: string;
    recommended_package: string;
    estimated_revenue_lift: string;
  }[];
  generated_proposal?: {
    title: string;
    executive_summary: string;
    recommended_tier_price: number;
    roi_projection: string;
  };
  outreach_pack?: {
    email_sequence: { step: number; subject: string; body: string }[];
    linkedin_inmail?: { subject: string; body: string };
    phone_pitch_script?: { opener: string; value_hook: string; close: string };
  };
}

/**
 * Runs full crawl and 6-domain SEO audit on a target URL.
 */
export async function auditWebsite(
  url: string,
  maxDepth: number = 2,
  maxPages: number = 10,
  javascript: boolean = false
): Promise<{ audit: WebsiteAuditResult | null; isLive: boolean; error: string | null }> {
  const result = await safeFetch<WebsiteAuditResult>(
    `${API_URLS.SDR}/api/v1/audit`,
    {
      method: 'POST',
      body: JSON.stringify({
        url,
        max_depth: maxDepth,
        max_pages: maxPages,
        javascript,
      }),
    },
    60000
  );

  return {
    audit: result.data,
    isLive: result.isLive,
    error: result.error,
  };
}

/**
 * Executes full SDR pipeline (Layers 2 through 8):
 * Normalization -> Parallel Audit -> Prompt Gen -> Opportunities -> Proposal -> Outreach Pack -> Lead Manager auto-registration.
 */
export async function executeFullSdrPipeline(prospectData: {
  company_name: string;
  website_url?: string;
  primary_contact_name?: string;
  primary_contact_email?: string;
  primary_contact_phone?: string;
  industry?: string;
  location?: string;
  source?: string;
}): Promise<{ result: SDRFullPipelineResult | null; isLive: boolean; error: string | null }> {
  const payload = {
    ...prospectData,
    source: prospectData.source || 'leadfinder+sdr',
  };

  const response = await safeFetch<SDRFullPipelineResult>(
    `${API_URLS.SDR}/api/v1/pipeline/process-target`,
    {
      method: 'POST',
      body: JSON.stringify(payload),
    },
    75000
  );

  return {
    result: response.data,
    isLive: response.isLive,
    error: response.error,
  };
}
