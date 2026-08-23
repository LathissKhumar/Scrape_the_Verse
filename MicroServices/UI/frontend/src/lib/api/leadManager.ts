/**
 * Lead Manager Microservice API Client (Port 8082).
 * System of Record, Deterministic 17-Stage State Machine, Tasks, Activities, Proposals, Meetings, and Twenty CRM Lifecycle.
 */

import { API_URLS, safeFetch } from './client';

export type LeadStageType =
  | 'DISCOVERED'
  | 'QUALIFIED'
  | 'RESEARCHED'
  | 'OPPORTUNITY_IDENTIFIED'
  | 'PROPOSAL_READY'
  | 'HUMAN_APPROVAL'
  | 'CONTACT_READY'
  | 'CONTACTED'
  | 'ENGAGED'
  | 'NOT_INTERESTED'
  | 'REQUEST_INFO'
  | 'MEETING_REQUESTED'
  | 'MEETING_SCHEDULED'
  | 'NEGOTIATION'
  | 'WON'
  | 'LOST'
  | 'DISQUALIFIED';

export interface LeadEntity {
  id: string;
  campaign_id?: string;
  company_name: string;
  industry?: string;
  location?: string;
  website_url?: string;
  primary_contact_name?: string;
  primary_contact_email?: string;
  primary_contact_phone?: string;
  stage: LeadStageType;
  fit_score?: number;
  opportunity_score?: number;
  recommended_services?: string[];
  metadata?: Record<string, unknown>;
  source: string;
  created_at: string;
  updated_at: string;
}

export interface PipelineStats {
  total_leads?: number;
  stage_counts?: Record<string, number>;
  [key: string]: unknown;
}

export interface ActivityEntity {
  id: string;
  lead_id: string;
  type: string;
  actor: string;
  summary: string;
  metadata?: Record<string, unknown>;
  created_at: string;
}

export interface TaskEntity {
  id: string;
  lead_id: string;
  type: string;
  status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED' | 'FAILED';
  due_at?: string;
  assigned_to: string;
  title?: string;
  description?: string;
  metadata?: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface OpportunityEntity {
  id: string;
  lead_id: string;
  type: string;
  score: number;
  problem_summary?: string;
  evidence?: Array<Record<string, unknown>>;
  recommended: boolean;
  status: string;
  metadata?: Record<string, unknown>;
  created_at: string;
}

export interface MeetingEntity {
  id: string;
  lead_id: string;
  conversation_id?: string;
  title: string;
  scheduled_at?: string;
  duration_minutes: number;
  timezone: string;
  status: 'REQUESTED' | 'PROPOSED' | 'CONFIRMED' | 'CANCELLED' | 'COMPLETED';
  meeting_url?: string;
  ics_content?: string;
  organizer_email?: string;
  attendee_email?: string;
  notes?: string;
  created_at: string;
}

export interface TwentyCrmStatus {
  crm: 'twenty';
  enabled: boolean;
  base_url: string;
  is_responsive: boolean;
  active_leases: number;
}

/**
 * Fetch all leads from Lead Manager.
 */
export async function getLeads(params?: {
  stage?: string;
  campaign_id?: string;
  limit?: number;
  offset?: number;
}): Promise<{ leads: LeadEntity[]; isLive: boolean; error: string | null }> {
  const query = new URLSearchParams();
  if (params?.stage) query.set('stage', params.stage);
  if (params?.campaign_id) query.set('campaign_id', params.campaign_id);
  if (params?.limit) query.set('limit', String(params.limit));
  if (params?.offset) query.set('offset', String(params.offset));

  const url = `${API_URLS.LEAD_MANAGER}/api/v1/leads${query.toString() ? `?${query.toString()}` : ''}`;
  const res = await safeFetch<LeadEntity[]>(url);

  return {
    leads: res.data || [],
    isLive: res.isLive,
    error: res.error,
  };
}

/**
 * Fetch pipeline stats.
 */
export async function getPipelineStats(): Promise<PipelineStats | null> {
  const res = await safeFetch<PipelineStats>(`${API_URLS.LEAD_MANAGER}/api/v1/leads/pipeline/stats`);
  return res.data;
}

/**
 * Fetch single lead by ID.
 */
export async function getLeadById(leadId: string): Promise<LeadEntity | null> {
  const res = await safeFetch<LeadEntity>(`${API_URLS.LEAD_MANAGER}/api/v1/leads/${leadId}`);
  return res.data;
}

/**
 * Create a new lead in Lead Manager.
 */
export async function createLead(leadData: Partial<LeadEntity>): Promise<{ lead: LeadEntity | null; error: string | null }> {
  const res = await safeFetch<LeadEntity>(`${API_URLS.LEAD_MANAGER}/api/v1/leads`, {
    method: 'POST',
    body: JSON.stringify(leadData),
  });
  return { lead: res.data, error: res.error };
}

/**
 * Update lead properties (e.g. stage, scores).
 */
export async function updateLead(
  leadId: string,
  updates: Partial<LeadEntity>
): Promise<{ lead: LeadEntity | null; error: string | null }> {
  const res = await safeFetch<LeadEntity>(`${API_URLS.LEAD_MANAGER}/api/v1/leads/${leadId}`, {
    method: 'PATCH',
    body: JSON.stringify(updates),
  });
  return { lead: res.data, error: res.error };
}

/**
 * Ingest lifecycle event to trigger deterministic state machine transition.
 */
export async function ingestLifecycleEvent(
  eventType: string,
  leadId: string,
  actor: string = 'human',
  payload: Record<string, unknown> = {}
): Promise<{ success: boolean; newStage?: string; error?: string }> {
  const res = await safeFetch<{
    status: string;
    new_stage?: string;
    transition_valid: boolean;
  }>(`${API_URLS.LEAD_MANAGER}/api/v1/events`, {
    method: 'POST',
    body: JSON.stringify({
      type: eventType,
      lead_id: leadId,
      actor,
      payload,
    }),
  });

  if (res.data) {
    return {
      success: true,
      newStage: res.data.new_stage,
    };
  }

  return {
    success: false,
    error: res.error || 'Failed to ingest lifecycle event',
  };
}

/**
 * Fetch lead activities.
 */
export async function getLeadActivities(leadId: string): Promise<ActivityEntity[]> {
  const res = await safeFetch<ActivityEntity[]>(`${API_URLS.LEAD_MANAGER}/api/v1/leads/${leadId}/activities`);
  return res.data || [];
}

/**
 * Fetch lead tasks.
 */
export async function getLeadTasks(leadId: string): Promise<TaskEntity[]> {
  const res = await safeFetch<TaskEntity[]>(`${API_URLS.LEAD_MANAGER}/api/v1/leads/${leadId}/tasks`);
  return res.data || [];
}

/**
 * Update task status.
 */
export async function updateTaskStatus(
  taskId: string,
  status: TaskEntity['status'],
  metadata?: Record<string, unknown>
): Promise<TaskEntity | null> {
  const res = await safeFetch<TaskEntity>(`${API_URLS.LEAD_MANAGER}/api/v1/tasks/${taskId}`, {
    method: 'PATCH',
    body: JSON.stringify({ status, metadata }),
  });
  return res.data;
}

/**
 * Fetch lead opportunities.
 */
export async function getLeadOpportunities(leadId: string): Promise<OpportunityEntity[]> {
  const res = await safeFetch<OpportunityEntity[]>(`${API_URLS.LEAD_MANAGER}/api/v1/leads/${leadId}/opportunities`);
  return res.data || [];
}

/**
 * Approve proposal (human-in-the-loop).
 */
export async function approveLeadProposal(leadId: string): Promise<LeadEntity | null> {
  const res = await safeFetch<LeadEntity>(`${API_URLS.LEAD_MANAGER}/api/v1/leads/${leadId}/approve-proposal`, {
    method: 'POST',
  });
  return res.data;
}

/**
 * Schedule calendar meeting.
 */
export async function scheduleMeeting(meetingData: {
  lead_id: string;
  title: string;
  scheduled_at: string;
  duration_minutes?: number;
  organizer_email?: string;
  attendee_email?: string;
  notes?: string;
}): Promise<{ meeting: MeetingEntity | null; error: string | null }> {
  const res = await safeFetch<MeetingEntity>(`${API_URLS.LEAD_MANAGER}/api/v1/meetings`, {
    method: 'POST',
    body: JSON.stringify(meetingData),
  });
  return { meeting: res.data, error: res.error };
}

/**
 * Twenty CRM Docker status & lifecycle controls.
 */
export async function getTwentyCrmStatus(): Promise<TwentyCrmStatus | null> {
  const res = await safeFetch<TwentyCrmStatus>(`${API_URLS.LEAD_MANAGER}/api/v1/crm/status`);
  return res.data;
}

export async function spinUpTwentyCrm(maxWait: number = 45): Promise<{ success: boolean; status: string }> {
  const res = await safeFetch<{ success: boolean; status: string }>(
    `${API_URLS.LEAD_MANAGER}/api/v1/crm/spin-up?max_wait=${maxWait}`,
    { method: 'POST' },
    60000
  );
  return res.data || { success: false, status: 'failed' };
}

export async function spinDownTwentyCrm(force: boolean = false): Promise<{ success: boolean; status: string }> {
  const res = await safeFetch<{ success: boolean; status: string }>(
    `${API_URLS.LEAD_MANAGER}/api/v1/crm/spin-down?force=${force}`,
    { method: 'POST' }
  );
  return res.data || { success: false, status: 'failed' };
}
