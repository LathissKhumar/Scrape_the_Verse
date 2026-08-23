/**
 * Voice Agent Microservice API Client (Port 8084).
 * Real-Time AI Telephony via Twilio Carrier PSTN, Multi-Turn Brain, Simulated Call Engine, and Meeting Auto-Bookings.
 */

import { API_URLS, safeFetch } from './client';

export interface VoiceConfigStatus {
  twilio_configured: boolean;
  twilio_phone_number?: string;
  personal_mobile_number?: string;
  public_base_url?: string;
  tts_voice?: string;
  barge_in_enabled?: boolean;
  setup_instructions?: string;
}

export interface CallSessionResult {
  id?: string;
  lead_id?: string;
  company_name: string;
  contact_name?: string;
  status: 'COMPLETED' | 'IN_PROGRESS' | 'SCHEDULED' | 'FAILED';
  disposition?: string;
  interest_score: number;
  transcript: Array<{ speaker: string; text: string; timestamp?: string }>;
  call_summary?: string;
  booked_meeting_time?: string;
  metadata?: Record<string, unknown>;
}

export interface OutboundCallResponse {
  success: boolean;
  call_sid?: string;
  status?: string;
  error?: string;
  details?: Record<string, unknown>;
}

/**
 * Fetch Twilio carrier telephony configuration status.
 */
export async function getVoiceConfig(): Promise<VoiceConfigStatus | null> {
  const res = await safeFetch<VoiceConfigStatus>(`${API_URLS.VOICE_AGENT}/api/v1/voice/config`);
  return res.data;
}

/**
 * Place a real outbound phone call via Twilio carrier.
 */
export async function initiateOutboundCall(params: {
  to_phone: string;
  lead_id?: string;
  company_name?: string;
  contact_name?: string;
  has_website?: boolean;
}): Promise<OutboundCallResponse> {
  const res = await safeFetch<OutboundCallResponse>(
    `${API_URLS.VOICE_AGENT}/api/v1/voice/call/initiate`,
    {
      method: 'POST',
      body: JSON.stringify(params),
    },
    20000
  );

  if (res.data) {
    return res.data;
  }

  return {
    success: false,
    error: res.error || 'Failed to initiate outbound call',
  };
}

/**
 * Send a 1-line verified audio test call to verify phone audio delivery.
 */
export async function sendTestCall(toPhone: string): Promise<OutboundCallResponse> {
  const res = await safeFetch<OutboundCallResponse>(
    `${API_URLS.VOICE_AGENT}/api/v1/voice/call/test`,
    {
      method: 'POST',
      body: JSON.stringify({ to_phone: toPhone }),
    },
    20000
  );

  return res.data || { success: false, error: res.error || 'Failed to send test call' };
}

/**
 * Executes a simulated multi-turn phone conversation for testing & development.
 */
export async function runSimulatedCall(params: {
  company_name: string;
  prospect_phone?: string;
  contact_name?: string;
  has_website?: boolean;
  lead_id?: string;
  simulated_prospect_responses?: string[];
}): Promise<{ session: CallSessionResult | null; isLive: boolean; error: string | null }> {
  const res = await safeFetch<CallSessionResult>(
    `${API_URLS.VOICE_AGENT}/api/v1/voice/simulate-call`,
    {
      method: 'POST',
      body: JSON.stringify(params),
    },
    45000
  );

  return {
    session: res.data,
    isLive: res.isLive,
    error: res.error,
  };
}
