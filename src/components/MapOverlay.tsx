import type { CycloneAnalysis } from '../types/analysis';

export function MapOverlay({ analysis }: { analysis: CycloneAnalysis }) {
  const last = analysis.track.at(-1);
  return (
    <div className="map-overlay-card">
      <span>48H FORECAST</span>
      <strong>{last ? `${last.latitude.toFixed(1)}°N · ${last.longitude.toFixed(1)}°E` : '—'}</strong>
      <small>{last ? `${last.wind_knots} kt predicted wind` : 'No forecast available'}</small>
    </div>
  );
}
