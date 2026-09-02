import type { AnalysisRequest, CycloneAnalysis } from '../types/analysis';

export async function runMockAnalysis(request: AnalysisRequest): Promise<CycloneAnalysis> {
  await new Promise((resolve) => window.setTimeout(resolve, 900));

  const sourceBonus = Math.min(request.sources.length * 0.015, 0.06);
  return {
    cyclone_detected: true,
    classification: {
      label: 'Very Severe Cyclonic Storm',
      confidence: Number((0.85 + sourceBonus).toFixed(2)),
    },
    intensity: { wind_knots: 82, pressure_hpa: 970 },
    center: { latitude: request.latitude, longitude: request.longitude },
    movement: { direction: 'NW', speed_knots: 12 },
    observed_track: [
      { hours: -18, latitude: 14.1, longitude: 79.7, wind_knots: 74 },
      { hours: -12, latitude: 14.5, longitude: 80.6, wind_knots: 77 },
      { hours: -6, latitude: 14.9, longitude: 81.5, wind_knots: 80 },
    ],
    track: [
      { hours: 6, latitude: 15.8, longitude: 83.1, wind_knots: 84, uncertainty_km: 45 },
      { hours: 12, latitude: 16.4, longitude: 83.9, wind_knots: 86, uncertainty_km: 70 },
      { hours: 24, latitude: 17.2, longitude: 85.1, wind_knots: 88, uncertainty_km: 105 },
      { hours: 36, latitude: 18.0, longitude: 86.2, wind_knots: 82, uncertainty_km: 145 },
      { hours: 48, latitude: 18.8, longitude: 87.1, wind_knots: 74, uncertainty_km: 190 },
    ],
    explainability: {
      labels: ['Deep convection', 'Curved banding', 'Eye structure'],
      heatmap_url: null,
    },
    model: {
      version: 'mock-v0.1',
      generated_at: new Date().toISOString(),
    },
  };
}
