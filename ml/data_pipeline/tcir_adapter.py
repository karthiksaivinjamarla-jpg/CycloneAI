"""TCIR-to-CycloneAI manifest adapter.

TCIR is distributed as a research dataset rather than a single standardized
CSV/NetCDF layout. This adapter therefore consumes a small metadata CSV that
maps each TCIR frame to a local file and timestamp, while keeping the actual
image reader independent from dataset download details.

Expected CSV columns:
storm_id,timestamp,channel,path

Optional columns latitude,longitude may be included when frame-center metadata
is available. The channel values are IR, WV, VIS, or MW.
"""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

from ml.data_pipeline.satellite_manifest import SatelliteFrame, validate_frame


def parse_timestamp(value: str) -> datetime:
    value = value.strip()
    normalized = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(f"Unsupported TCIR timestamp: {value!r}") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def load_tcir_metadata(path: str | Path) -> list[SatelliteFrame]:
    """Read a TCIR metadata CSV and validate every frame contract."""
    frames: list[SatelliteFrame] = []
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"storm_id", "timestamp", "channel", "path"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            missing = sorted(required - set(reader.fieldnames or []))
            raise ValueError(f"TCIR metadata missing columns: {missing}")

        for row in reader:
            latitude = float(row["latitude"]) if row.get("latitude", "").strip() else None
            longitude = float(row["longitude"]) if row.get("longitude", "").strip() else None
            frame = SatelliteFrame(
                storm_id=row["storm_id"].strip(),
                timestamp=parse_timestamp(row["timestamp"]),
                source="TCIR",
                channel=row["channel"].strip().upper(),
                path=row["path"].strip(),
                latitude=latitude,
                longitude=longitude,
            )
            validate_frame(frame)
            frames.append(frame)

    return sorted(frames, key=lambda frame: (frame.storm_id, frame.timestamp, frame.channel))


def write_manifest(frames: list[SatelliteFrame], output: str | Path) -> None:
    """Write normalized JSONL metadata for the existing pipeline."""
    import json

    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8") as handle:
        for frame in frames:
            handle.write(json.dumps({
                "storm_id": frame.storm_id,
                "timestamp": frame.timestamp.isoformat(),
                "source": frame.source,
                "channel": frame.channel,
                "path": frame.path,
                "latitude": frame.latitude,
                "longitude": frame.longitude,
            }) + "\n")
