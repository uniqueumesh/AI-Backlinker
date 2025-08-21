/**
 * Email Generation API service - handles email creation operations
 */
import { apiRequest } from './base';
import type { 
  EmailGenerateStartResponse, 
  EmailGenerateStatus 
} from './types';

/**
 * Start email generation for selected research results
 */
export async function emailsGenerateStart(params: {
  research_job_id: string;
  selected_urls?: string[];
  subject: string;
  take: number;
  provider: 'gemini' | 'openai';
  model?: string;
  your_name?: string;
  your_email?: string;
}): Promise<EmailGenerateStartResponse> {
  return apiRequest<EmailGenerateStartResponse>('/emails/generate/start', {
    method: 'POST',
    body: JSON.stringify(params),
  });
}

/**
 * Get the status and results of an email generation job
 */
export async function getEmailsGenerateStatus(
  jobId: string
): Promise<EmailGenerateStatus> {
  return apiRequest<EmailGenerateStatus>(`/emails/generate/status/${jobId}`);
}
