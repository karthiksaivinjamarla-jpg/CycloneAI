import type { AnalysisRequest, CycloneAnalysis } from '../types/analysis';
import { runMockAnalysis } from './mockModel';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, '');

/** Stable frontend boundary for FastAPI/ML inference. */
export async function runAnalysis(request: AnalysisRequest): Promise<CycloneAnalysis> {
  if (!API_BASE_URL) return runMockAnalysis(request);

  const response = await fetch(`${API_BASE_URL}/api/v1/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    let detail = '';
    try {
      const payload = await response.json() as { detail?: string };
      detail = payload.detail ? `: ${payload.detail}` : '';
    } catch {
      // Keep the HTTP status as the useful fallback.
    }
    throw new Error(`Model API request failed (${response.status})${detail}`);
  }

  return response.json() as Promise<CycloneAnalysis>;
}
