/**
 * Research API service - handles backlink research operations
 */
import { apiRequest } from './base';
import type { ResearchStartResponse, ResearchStatus } from './types';

/**
 * Start a new research job
 */
export async function startResearch(
  keyword: string, 
  maxResults = 10
): Promise<ResearchStartResponse> {
  return apiRequest<ResearchStartResponse>('/research/start', {
    method: 'POST',
    body: JSON.stringify({ 
      keyword, 
      max_results: maxResults 
    }),
  });
}

/**
 * Get the status and results of a research job
 */
export async function getResearchStatus(
  jobId: string
): Promise<ResearchStatus> {
  return apiRequest<ResearchStatus>(`/research/status/${jobId}`);
}
