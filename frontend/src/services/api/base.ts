/**
 * Base API configuration and utilities
 */

// Base URL configuration
export const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

/**
 * Generic error handler for API responses
 */
export async function handleApiError(response: Response): Promise<never> {
  const text = await response.text().catch(() => '');
  throw new Error(`${response.statusText} (${response.status}): ${text}`);
}

/**
 * Generic API request wrapper
 */
export async function apiRequest<T>(
  endpoint: string, 
  options: RequestInit = {}
): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    await handleApiError(response);
  }

  return response.json();
}
