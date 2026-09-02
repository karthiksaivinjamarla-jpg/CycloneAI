from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .ibtracs_loader import TrackRecord


@dataclass(frozen=True)
class NormalizedObservation:
    storm_id: str
    name: str
    basin: str
    timestamp: datetime
    latitude: float
    longitude: float
    wind_knots: float | None
    pressure_hpa: float | None


def normalize(records: list[TrackRecord]) -> list[NormalizedObservation]:
    """Sort records into a stable storm/time order for downstream processing."""
    normalized = [
        NormalizedObservation(
            storm_id=r.storm_id,
            name=r.name,
            basin=r.basin,
            timestamp=r.timestamp,
            latitude=r.latitude,
            longitude=r.longitude,
            wind_knots=r.wind_knots,
            pressure_hpa=r.pressure_hpa,
        )
        for r in records
        if r.storm_id
    ]
    return sorted(normalized, key=lambda x: (x.storm_id, x.timestamp))
