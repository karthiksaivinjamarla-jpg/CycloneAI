import type { TrackPoint } from '../types/analysis';

export function ForecastBadge({ point }: { point?: TrackPoint }) {
  if (!point) return null;
  return <span className="forecast-badge">+{point.hours}h · {point.wind_knots} kt</span>;
}
