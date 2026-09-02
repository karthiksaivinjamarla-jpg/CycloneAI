import { useEffect, useRef } from 'react';
import * as L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import './CycloneMap.css';
import type { CycloneAnalysis, TrackPoint } from '../types/analysis';

type Props = {
  analysis: CycloneAnalysis;
};

const observedFallback: TrackPoint[] = [
  { hours: -18, latitude: 14.1, longitude: 79.7, wind_knots: 74 },
  { hours: -12, latitude: 14.5, longitude: 80.6, wind_knots: 77 },
  { hours: -6, latitude: 14.9, longitude: 81.5, wind_knots: 80 },
];

function point(lat: number, lon: number): L.LatLngExpression {
  return [lat, lon];
}

function uncertaintyPolygon(track: TrackPoint[]): L.LatLngExpression[] {
  if (track.length < 2) return [];
  const left: L.LatLngExpression[] = [];
  const right: L.LatLngExpression[] = [];

  track.forEach((item, index) => {
    const previous = track[Math.max(0, index - 1)];
    const next = track[Math.min(track.length - 1, index + 1)];
    const dy = next.latitude - previous.latitude;
    const dx = (next.longitude - previous.longitude) * Math.cos((item.latitude * Math.PI) / 180);
    const length = Math.hypot(dx, dy) || 1;
    const radiusKm = item.uncertainty_km ?? 35 + index * 18;
    const latOffset = (radiusKm / 111) * (dx / length);
    const lonOffset = (radiusKm / (111 * Math.cos((item.latitude * Math.PI) / 180))) * (-dy / length);
    left.push(point(item.latitude + latOffset, item.longitude + lonOffset));
    right.push(point(item.latitude - latOffset, item.longitude - lonOffset));
  });

  return [...left, ...right.reverse()];
}

export function CycloneMap({ analysis }: Props) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<L.Map | null>(null);

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    const map = L.map(containerRef.current, {
      center: [16.1, 83.8],
      zoom: 5,
      zoomControl: true,
      attributionControl: true,
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 10,
      attribution: '&copy; OpenStreetMap contributors',
    }).addTo(map);

    mapRef.current = map;
    setTimeout(() => map.invalidateSize(), 0);

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    map.eachLayer((layer) => {
      if (!(layer instanceof L.TileLayer)) map.removeLayer(layer);
    });

    const current = point(analysis.center.latitude, analysis.center.longitude);
    const forecast = [current, ...analysis.track.map((item) => point(item.latitude, item.longitude))];
    const observed = (analysis.observed_track?.length ? analysis.observed_track : observedFallback).map((item) => point(item.latitude, item.longitude));

    L.polyline(observed, { color: '#73879a', weight: 3, opacity: 0.9 }).addTo(map);
    L.polyline(forecast, { color: '#18c7f4', weight: 4, opacity: 1, dashArray: '8 8' }).addTo(map);

    const corridor = uncertaintyPolygon(analysis.track);
    if (corridor.length) {
      L.polygon(corridor, {
        color: '#18c7f4',
        weight: 1,
        opacity: 0.35,
        fillColor: '#18c7f4',
        fillOpacity: 0.09,
      }).addTo(map);
    }

    observed.forEach((position) => {
      L.circleMarker(position, { radius: 4, color: '#d7e1e8', fillColor: '#8fa5b5', fillOpacity: 1, weight: 1 }).addTo(map);
    });

    analysis.track.forEach((item) => {
      const marker = L.circleMarker(point(item.latitude, item.longitude), {
        radius: 5,
        color: '#0b2a3b',
        fillColor: '#18c7f4',
        fillOpacity: 1,
        weight: 2,
      }).addTo(map);
      marker.bindTooltip(`+${item.hours}h · ${item.wind_knots} kt`, { direction: 'top', offset: [0, -5] });
    });

    L.marker(current, {
      icon: L.divIcon({
        className: 'cyclone-center-marker',
        html: '<span><i></i><b></b></span>',
        iconSize: [62, 62],
        iconAnchor: [31, 31],
      }),
    }).addTo(map).bindTooltip('Current cyclone center', { direction: 'top', offset: [0, -25] });

    const bounds = L.latLngBounds([...observed, ...forecast]);
    map.fitBounds(bounds.pad(0.18), { animate: true, duration: 0.6 });
  }, [analysis]);

  return <div ref={containerRef} className="cyclone-map" aria-label="Interactive Bay of Bengal cyclone map" />;
}
