"""Manifest and tensor-shape contract for multi-source satellite inputs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

SUPPORTED_CHANNELS = ("IR", "WV", "VIS", "MW")


@dataclass(frozen=True)
class SatelliteFrame:
    storm_id: str
    timestamp: datetime
    source: str
    channel: str
    path: str
    latitude: float | None = None
    longitude: float | None = None


def validate_frame(frame: SatelliteFrame) -> None:
    if not frame.storm_id:
        raise ValueError("storm_id is required")
    if frame.channel not in SUPPORTED_CHANNELS:
        raise ValueError(f"unsupported channel: {frame.channel}")
    if not frame.source:
        raise ValueError("source is required")
    if not frame.path:
        raise ValueError("path is required")
    if frame.latitude is not None and not -90 <= frame.latitude <= 90:
        raise ValueError("latitude must be between -90 and 90")
    if frame.longitude is not None and not -180 <= frame.longitude <= 180:
        raise ValueError("longitude must be between -180 and 180")


def group_by_timestamp(frames: list[SatelliteFrame]) -> dict[datetime, list[SatelliteFrame]]:
    """Group validated frames so IR/WV/VIS/MW can be fused later."""
    for frame in frames:
        validate_frame(frame)
    grouped: dict[datetime, list[SatelliteFrame]] = {}
    for frame in frames:
        grouped.setdefault(frame.timestamp, []).append(frame)
    return {timestamp: sorted(items, key=lambda item: item.channel) for timestamp, items in sorted(grouped.items())}
