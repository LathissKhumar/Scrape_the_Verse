/**
 * leadfinder Microservice API Client (Port 8000).
 * Connects to c:\Projects\Scrape_the_Verse\MicroServices\leadfinder
 * Handles Google Maps discovery, Bright Data B2B leads, Scraper jobs, and DCA collector registry.
 */

import { API_URLS, safeFetch } from "./client";

export interface GMapLeadItem {
  name: string;
  category?: string;
  address?: string;
  phone?: string;
  website?: string;
  rating?: number;
  reviews_count?: number;
  place_id?: string;
  latitude?: number;
  longitude?: number;
}

export interface BrightDataLeadItem {
  company_name: string;
  industry?: string;
  location?: string;
  website?: string;
  contact_name?: string;
  contact_email?: string;
  contact_phone?: string;
  title?: string;
  revenue?: string;
  employee_count?: string;
  linkedin_url?: string;
}

export interface ScraperRecord {
  id: string;
  collector_id: string;
  name: string;
  target_domain: string;
  status: "READY" | "CREATING" | "HEALING" | "ERROR";
  records_extracted: number;
  health_score: number;
  last_healed?: string;
  healing_attempts: number;
}

export interface JobStatusResponse {
  job_id: string;
  status: "queued" | "running" | "completed" | "failed";
  total_urls: number;
  processed_urls?: number;
  records_extracted?: number;
  error?: string;
}

/**
 * Discovers local business leads using Google Maps agent from leadfinder.
 */
export async function searchGoogleMapsLeads(
  query: string,
  location?: string,
): Promise<{
  leads: GMapLeadItem[];
  total: number;
  isLive: boolean;
  error: string | null;
}> {
  const fullQuery = location ? `${query} in ${location}` : query;
  const result = await safeFetch<{
    query: string;
    category: string;
    location: string;
    total_leads: number;
    leads: GMapLeadItem[];
  }>(
    `${API_URLS.LEADFINDER}/api/v1/gmaps/leads`,
    {
      method: "POST",
      body: JSON.stringify({ query: fullQuery }),
    },
    45000,
  );

  if (result.data && result.data.leads) {
    return {
      leads: result.data.leads,
      total: result.data.total_leads || result.data.leads.length,
      isLive: true,
      error: null,
    };
  }

  return {
    leads: [],
    total: 0,
    isLive: result.isLive,
    error: result.error || "Failed to fetch Google Maps leads from leadfinder",
  };
}

/**
 * Discovers B2B leads using Bright Data pipeline from leadfinder.
 */
export async function searchBrightDataLeads(
  query: string,
  enrich: boolean = true,
): Promise<{
  leads: BrightDataLeadItem[];
  total: number;
  isLive: boolean;
  error: string | null;
}> {
  const result = await safeFetch<{
    query: string;
    total_leads: number;
    leads: BrightDataLeadItem[];
  }>(
    `${API_URLS.LEADFINDER}/api/v1/brightdata/leads`,
    {
      method: "POST",
      body: JSON.stringify({
        query,
        metadata: { enrich },
      }),
    },
    60000,
  );

  if (result.data && result.data.leads) {
    return {
      leads: result.data.leads,
      total: result.data.total_leads || result.data.leads.length,
      isLive: true,
      error: null,
    };
  }

  return {
    leads: [],
    total: 0,
    isLive: result.isLive,
    error: result.error || "Failed to fetch Bright Data leads from leadfinder",
  };
}

/**
 * Submits an asynchronous background scraping job to leadfinder.
 */
export async function submitScrapingJob(
  query: string,
  targetUrls: string[],
): Promise<{
  jobId: string | null;
  status: string;
  isLive: boolean;
  error: string | null;
}> {
  const result = await safeFetch<{
    job_id: string;
    status: string;
    total_urls: number;
    status_url: string;
  }>(`${API_URLS.LEADFINDER}/api/v1/jobs`, {
    method: "POST",
    body: JSON.stringify({
      query,
      target_urls: targetUrls,
    }),
  });

  if (result.data) {
    return {
      jobId: result.data.job_id,
      status: result.data.status,
      isLive: true,
      error: null,
    };
  }

  return {
    jobId: null,
    status: "failed",
    isLive: result.isLive,
    error: result.error || "Failed to submit scraping job to leadfinder",
  };
}

/**
 * Checks progress of an async scraping job in leadfinder.
 */
export async function getScrapingJobStatus(
  jobId: string,
): Promise<JobStatusResponse | null> {
  const result = await safeFetch<JobStatusResponse>(
    `${API_URLS.LEADFINDER}/api/v1/jobs/${jobId}`,
  );
  return result.data;
}

/**
 * Lists DCA collectors in the leadfinder self-healing registry.
 */
export async function listRegistryScrapers(): Promise<{
  scrapers: ScraperRecord[];
  isLive: boolean;
}> {
  const result = await safeFetch<{ total: number; scrapers: ScraperRecord[] }>(
    `${API_URLS.LEADFINDER}/scrapers`,
  );

  if (result.data && result.data.scrapers) {
    return { scrapers: result.data.scrapers, isLive: true };
  }

  return { scrapers: [], isLive: result.isLive };
}

/**
 * Triggers self-healing on a broken Bright Data DCA collector in leadfinder.
 */
export async function healCollector(
  collectorId: string,
  failureDescription: string,
): Promise<{ success: boolean; message: string }> {
  const result = await safeFetch<{
    collector_id: string;
    status: string;
    repair_summary?: string;
  }>(
    `${API_URLS.LEADFINDER}/scrapers/heal`,
    {
      method: "POST",
      body: JSON.stringify({
        collector_id: collectorId,
        failure_description: failureDescription,
      }),
    },
    45000,
  );

  if (result.data && result.data.status === "success") {
    return {
      success: true,
      message:
        result.data.repair_summary ||
        `Collector ${collectorId} successfully repaired.`,
    };
  }

  return {
    success: false,
    message: result.error || "Self-healing request failed in leadfinder",
  };
}
