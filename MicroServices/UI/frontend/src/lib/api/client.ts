/**
 * Core API Client & Microservices Gateway Configuration.
 * Handles timeouts, error formatting, live health probing, and graceful mock fallbacks.
 * Connects to MicroServices/leadfinder (:8000), SDR (:8081), Lead_Manager (:8082), Voice_Agent (:8084).
 */

export const SERVICE_PORTS = {
  LEADFINDER: 8000,
  SDR: 8081,
  LEAD_MANAGER: 8082,
  VOICE_AGENT: 8084,
};

export const API_URLS = {
  LEADFINDER: process.env.NEXT_PUBLIC_LEADFINDER_URL || `http://localhost:${SERVICE_PORTS.LEADFINDER}`,
  SDR: process.env.NEXT_PUBLIC_SDR_URL || `http://localhost:${SERVICE_PORTS.SDR}`,
  LEAD_MANAGER: process.env.NEXT_PUBLIC_LEAD_MANAGER_URL || `http://localhost:${SERVICE_PORTS.LEAD_MANAGER}`,
  VOICE_AGENT: process.env.NEXT_PUBLIC_VOICE_AGENT_URL || `http://localhost:${SERVICE_PORTS.VOICE_AGENT}`,
};

export interface ServiceHealthStatus {
  service: 'leadfinder' | 'sdr' | 'lead_manager' | 'voice_agent';
  name: string;
  port: number;
  isOnline: boolean;
  latencyMs?: number;
  details?: Record<string, unknown>;
}

/**
 * Safe fetch with configurable timeout and error parsing.
 */
export async function safeFetch<T>(
  url: string,
  options: RequestInit = {},
  timeoutMs: number = 25000
): Promise<{ data: T | null; error: string | null; isLive: boolean }> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
        ...(options.headers || {}),
      },
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      let errorDetail = `HTTP ${response.status}: ${response.statusText}`;
      try {
        const errorJson = await response.json();
        errorDetail = errorJson.detail || errorJson.message || errorDetail;
      } catch {
        // use status text if body not json
      }
      return { data: null, error: errorDetail, isLive: true };
    }

    const contentType = response.headers.get('content-type') || '';
    if (contentType.includes('application/json')) {
      const data = await response.json();
      return { data, error: null, isLive: true };
    } else {
      const text = await response.text();
      return { data: text as unknown as T, error: null, isLive: true };
    }
  } catch (err: unknown) {
    clearTimeout(timeoutId);
    const error = err as Error;
    const isAbort = error.name === 'AbortError';
    const message = isAbort
      ? `Request timed out after ${timeoutMs}ms`
      : error.message || 'Network connection failed (Service offline or CORS blocked)';
    return { data: null, error: message, isLive: false };
  }
}

/**
 * Probe all 4 backend microservices concurrently for health status.
 */
export async function checkAllServicesHealth(): Promise<Record<string, ServiceHealthStatus>> {
  const probe = async (
    service: ServiceHealthStatus['service'],
    name: string,
    port: number,
    baseUrl: string
  ): Promise<ServiceHealthStatus> => {
    const startTime = performance.now();
    const result = await safeFetch<Record<string, unknown>>(`${baseUrl}/health`, { method: 'GET' }, 3500);
    const latencyMs = Math.round(performance.now() - startTime);

    return {
      service,
      name,
      port,
      isOnline: result.isLive && result.data !== null && (result.data.status === 'healthy' || result.data.status === 'ok'),
      latencyMs,
      details: result.data || undefined,
    };
  };

  const [leadfinder, sdr, leadManager, voiceAgent] = await Promise.all([
    probe('leadfinder', 'leadfinder (Port 8000)', SERVICE_PORTS.LEADFINDER, API_URLS.LEADFINDER),
    probe('sdr', 'SDR Intelligence', SERVICE_PORTS.SDR, API_URLS.SDR),
    probe('lead_manager', 'Lead Manager', SERVICE_PORTS.LEAD_MANAGER, API_URLS.LEAD_MANAGER),
    probe('voice_agent', 'Voice Agent', SERVICE_PORTS.VOICE_AGENT, API_URLS.VOICE_AGENT),
  ]);

  return {
    leadfinder,
    sdr,
    lead_manager: leadManager,
    voice_agent: voiceAgent,
  };
}
