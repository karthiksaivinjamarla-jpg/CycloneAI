from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from .normalize import NormalizedObservation
from .satellite_manifest import SatelliteFrame


@dataclass(frozen=True)
class JoinedSample:
    storm_id: str
    timestamp: str
    latitude: float
    longitude: float
    channels: dict[str, str]


def join_nearest_satellite(
    observations: list[NormalizedObservation],
    frames: list[SatelliteFrame],
    tolerance_minutes: int = 90,
) -> list[JoinedSample]:
    """Attach the nearest available frame for each channel to a track point.

    Only frames from the same storm are considered. A channel is omitted when
    no frame falls within the configured time tolerance.
    """
    by_storm: dict[str, list[SatelliteFrame]] = {}
    for frame in frames:
        by_storm.setdefault(frame.storm_id, []).append(frame)

    tolerance = timedelta(minutes=tolerance_minutes)
    samples: list[JoinedSample] = []

    for observation in observations:
        candidates = by_storm.get(observation.storm_id, [])
        channels: dict[str, str] = {}
        for channel in ("IR", "WV", "VIS", "MW"):
            same_channel = [f for f in candidates if f.channel == channel]
            if not same_channel:
                continue
            nearest = min(same_channel, key=lambda f: abs(f.timestamp - observation.timestamp))
            if abs(nearest.timestamp - observation.timestamp) <= tolerance:
                channels[channel] = nearest.path

        samples.append(
            JoinedSample(
                storm_id=observation.storm_id,
                timestamp=observation.timestamp.isoformat(),
                latitude=observation.latitude,
                longitude=observation.longitude,
                channels=channels,
            )
        )

    return samples
