"""Utilities for adding cyclone-negative satellite samples.

A detection model needs both positive cyclone frames and negative frames. This
module builds negatives from satellite metadata rows whose storm_id is not in
the supplied cyclone-track IDs. It does not download or modify raw data.
"""

from __future__ import annotations

from dataclasses import replace

from ml.data_pipeline.satellite_manifest import SatelliteFrame


def build_negative_frames(
    frames: list[SatelliteFrame],
    cyclone_storm_ids: set[str],
) -> list[SatelliteFrame]:
    """Return validated satellite frames that are outside known cyclone IDs."""
    return [
        replace(frame, source=f"{frame.source}:negative")
        for frame in frames
        if frame.storm_id not in cyclone_storm_ids
    ]


def build_detection_record(frame: SatelliteFrame, *, detected: bool) -> dict[str, object]:
    """Create the minimal JSON-serializable detection record."""
    return {
        "storm_id": frame.storm_id,
        "timestamp": frame.timestamp.isoformat(),
        "image_paths": {frame.channel: frame.path},
        "detected": detected,
        "class_index": 0,
        "wind_knots": 0.0,
        "track_offsets": [[0.0, 0.0]],
    }
