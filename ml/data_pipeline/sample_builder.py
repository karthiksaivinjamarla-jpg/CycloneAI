from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from .normalize import NormalizedObservation


@dataclass(frozen=True)
class ForecastSample:
    storm_id: str
    input_times: tuple[str, ...]
    center_latitude: float
    center_longitude: float
    target_latitude: float
    target_longitude: float
    forecast_hours: int


def build_samples(
    observations: list[NormalizedObservation],
    input_steps: int = 4,
    forecast_hours: int = 24,
) -> list[ForecastSample]:
    """Build simple equally-spaced track samples for a first baseline.

    This function uses track records only. Satellite tensors will be joined in
    a later preprocessing stage once the satellite source format is fixed.
    """
    by_storm: dict[str, list[NormalizedObservation]] = {}
    for item in observations:
        by_storm.setdefault(item.storm_id, []).append(item)

    samples: list[ForecastSample] = []
    target_delta = timedelta(hours=forecast_hours)

    for storm_id, track in by_storm.items():
        for index in range(input_steps - 1, len(track)):
            history = track[index - input_steps + 1 : index + 1]
            target_time = history[-1].timestamp + target_delta
            target = next((item for item in track if item.timestamp == target_time), None)
            if target is None:
                continue

            samples.append(
                ForecastSample(
                    storm_id=storm_id,
                    input_times=tuple(item.timestamp.isoformat() for item in history),
                    center_latitude=history[-1].latitude,
                    center_longitude=history[-1].longitude,
                    target_latitude=target.latitude,
                    target_longitude=target.longitude,
                    forecast_hours=forecast_hours,
                )
            )

    return samples
