const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

export type ResearchStartResponse = { job_id: string };
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

export type EmailGenerateStartResponse = { job_id: string };
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

export async function startResearch(keyword: string, maxResults = 10): Promise<ResearchStartResponse> {
  const res = await fetch(`${API_BASE}/research/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ keyword, max_results: maxResults }),
  });
  if (!res.ok) {
    const txt = await res.text().catch(() => '');
    throw new Error(`Start research failed (${res.status}): ${txt}`);
  }
  return res.json();
}

export async function getResearchStatus(jobId: string): Promise<ResearchStatus> {
  const res = await fetch(`${API_BASE}/research/status/${jobId}`);
  if (!res.ok) {
    const txt = await res.text().catch(() => '');
    throw new Error(`Status failed (${res.status}): ${txt}`);
  }
  return res.json();
}

export async function emailsGenerateStart(params: {
  research_job_id: string;
  selected_urls?: string[];
  subject: string;
  take: number;
  provider: 'gemini' | 'openai';
  model?: string;
}): Promise<EmailGenerateStartResponse> {
  const res = await fetch(`${API_BASE}/emails/generate/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  if (!res.ok) {
    const txt = await res.text().catch(() => '');
    throw new Error(`Start email generation failed (${res.status}): ${txt}`);
  }
  return res.json();
}

export async function getEmailsGenerateStatus(jobId: string): Promise<EmailGenerateStatus> {
  const res = await fetch(`${API_BASE}/emails/generate/status/${jobId}`);
  if (!res.ok) {
    const txt = await res.text().catch(() => '');
    throw new Error(`Email generation status failed (${res.status}): ${txt}`);
  }
  return res.json();
}


