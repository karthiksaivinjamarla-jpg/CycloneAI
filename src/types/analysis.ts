export type SatelliteSource = 'IR' | 'WV' | 'VIS' | 'MW';

export interface TrackPoint {
  hours: number;
  latitude: number;
  longitude: number;
  wind_knots: number;
  uncertainty_km?: number;
}

export interface CycloneAnalysis {
  cyclone_detected: boolean;
  classification: { label: string; confidence: number };
  intensity: { wind_knots: number; pressure_hpa: number };
  center: { latitude: number; longitude: number };
  movement: { direction: string; speed_knots: number };
  observed_track?: TrackPoint[];
  track: TrackPoint[];
  explainability: { labels: string[]; heatmap_url?: string | null };
  model: { version: string; generated_at: string };
}

export interface AnalysisRequest {
  timestamp: string;
  latitude: number;
  longitude: number;
  sources: SatelliteSource[];
}
