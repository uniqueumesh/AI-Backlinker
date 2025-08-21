/**
 * Type definitions for all API operations
 */

// Research API Types
export type ResearchStartResponse = { 
  job_id: string 
};

export type ResearchStatus = {
  job_id: string;
  status: 'queued' | 'running' | 'done' | 'error';
  progress: number;
  error?: string | null;
  results?: Array<{
    url: string;
    domain: string;
    title: string;
    contact_email: string;
    contact_form_url?: string;
    guidelines_url?: string;
    context_source?: string;
    page_excerpt?: string;
  }> | null;
};

// Email Generation API Types
export type EmailGenerateStartResponse = { 
  job_id: string 
};

export type EmailRow = {
  to_email: string;
  subject: string;
  body: string;
  url?: string;
  domain?: string;
  title?: string;
  context_source?: string;
  excerpt_chars?: number;
  status?: string;
  note?: string;
  provider?: string;
  model?: string;
};

export type EmailGenerateStatus = {
  job_id: string;
  status: 'queued' | 'running' | 'done' | 'error';
  progress: number;
  error?: string | null;
  results?: EmailRow[] | null;
  saved_csv_path?: string | null;
};

// Send API Types
export type SendStartResponse = { 
  job_id: string 
};

export type SendOutcomeRow = { 
  row?: number | string; 
  to_email?: string; 
  status?: string; 
  code?: string; 
  message?: string 
};

export type SendStatusResponse = {
  job_id: string;
  status: 'queued' | 'running' | 'done' | 'error';
  progress: number;
  error?: string | null;
  results?: SendOutcomeRow[] | null;
  saved_csv_path?: string | null;
};
