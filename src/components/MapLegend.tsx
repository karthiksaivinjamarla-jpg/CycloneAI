export function MapLegend() {
  return (
    <div className="map-legend">
      <span><i className="legend-observed" /> Observed</span>
      <span><i className="legend-ai" /> AI forecast</span>
      <span><i className="legend-band" /> Uncertainty</span>
    </div>
  );
}
