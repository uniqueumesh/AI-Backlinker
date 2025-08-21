/**
 * Send API service - handles email sending operations
 */
import { apiRequest } from './base';
import type { SendStartResponse, SendStatusResponse } from './types';

/**
 * Start sending emails using the specified provider
 */
export async function sendStart(params: {
  provider: 'sendgrid' | 'mailersend' | 'smtp';
  from_email: string;
  rows?: Array<{ to_email: string; subject: string; body: string }>;
  in_csv?: string;
  rate_limit_per_sec?: number;
  dry_run?: boolean;
  sandbox?: boolean;
  smtp_host?: string;
  smtp_port?: number;
  smtp_user?: string;
  smtp_pass?: string;
}): Promise<SendStartResponse> {
  return apiRequest<SendStartResponse>('/send/start', {
    method: 'POST',
    body: JSON.stringify(params),
  });
}

/**
 * Get the status and results of a send job
 */
export async function getSendStatus(
  jobId: string
): Promise<SendStatusResponse> {
  return apiRequest<SendStatusResponse>(`/send/status/${jobId}`);
}
