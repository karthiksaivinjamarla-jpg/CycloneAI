import { Activity } from 'lucide-react';

export function MapStatus() {
  return (
    <div className="map-status-badge">
      <Activity size={13} />
      <span>Interactive map · Prototype</span>
    </div>
  );
}
