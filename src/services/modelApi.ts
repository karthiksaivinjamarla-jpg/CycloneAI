import type { AnalysisRequest, CycloneAnalysis } from '../types/analysis';
import { runMockAnalysis } from './mockModel';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL as string | undefined;

/**
 * Stable frontend boundary for the future FastAPI/ML service.
 * Set VITE_API_BASE_URL to use the real backend; otherwise the mock adapter is used.
 */
export async function runAnalysis(request: AnalysisRequest): Promise<CycloneAnalysis> {
  if (!API_BASE_URL) return runMockAnalysis(request);

  const response = await fetch(`${API_BASE_URL}/api/v1/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`Model API request failed (${response.status})`);
  }

  return response.json() as Promise<CycloneAnalysis>;
}
