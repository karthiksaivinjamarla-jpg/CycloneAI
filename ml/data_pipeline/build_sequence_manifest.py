"""Build labeled temporal sequence manifests from fused satellite frames + IBTrACS."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path

from ml.data_pipeline.ibtracs_loader import load_ibtracs_csv
from ml.data_pipeline.labels import classify_wind, track_offsets
from ml.data_pipeline.sequence_builder import build_sequences


def read_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def parse_time(value: object) -> datetime:
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    return parsed.replace(tzinfo=None) if parsed.tzinfo else parsed


def build_labeled_sequences(
    fused_frames: list[dict[str, object]],
    tracks: list[object],
    sequence_length: int = 4,
    cadence_hours: int = 3,
    tolerance_minutes: int = 90,
    forecast_hours: int = 24,
) -> list[dict[str, object]]:
    """Create one training record per eligible sequence endpoint.

    The sequence contains historical satellite frames. Labels describe the
    endpoint observation, while track_offsets contains the future displacement
    at the requested forecast horizon.
    """
    sequences = build_sequences(
        fused_frames,
        sequence_length=sequence_length,
        cadence_hours=cadence_hours,
        tolerance_minutes=tolerance_minutes,
    )

    by_storm: dict[str, list[object]] = {}
    for track in tracks:
        by_storm.setdefault(track.storm_id, []).append(track)
    for rows in by_storm.values():
        rows.sort(key=lambda row: row.timestamp)

    tolerance = timedelta(minutes=tolerance_minutes)
    output: list[dict[str, object]] = []

    for sequence in sequences:
        storm_id = str(sequence["storm_id"])
        rows = by_storm.get(storm_id)
        if not rows:
            continue
        endpoint_time = parse_time(sequence["timestamp"])
        current = min(rows, key=lambda row: abs(row.timestamp - endpoint_time))
        if abs(current.timestamp - endpoint_time) > tolerance or current.wind_knots is None:
            continue

        target_time = current.timestamp + timedelta(hours=forecast_hours)
        future = min(rows, key=lambda row: abs(row.timestamp - target_time))
        if abs(future.timestamp - target_time) > tolerance:
            continue

        class_idx, class_label = classify_wind(current.wind_knots)
        frames = sequence["frames"]
        output.append({
            "storm_id": storm_id,
            "timestamp": sequence["timestamp"],
            "frames": frames,
            "sequence_length": sequence_length,
            "cadence_hours": cadence_hours,
            "detected": True,
            "class_index": class_idx,
            "class_label": class_label,
            "wind_knots": float(current.wind_knots),
            "center_latitude": float(current.latitude),
            "center_longitude": float(current.longitude),
            "target_latitude": float(future.latitude),
            "target_longitude": float(future.longitude),
            "track_offsets": [track_offsets(current.latitude, current.longitude, future.latitude, future.longitude)],
            "forecast_hours": forecast_hours,
            "target_timestamp": future.timestamp.isoformat(),
        })

    return output


def write_jsonl(records: list[dict[str, object]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build labeled CNN-GRU sequence manifest")
    parser.add_argument("fused_manifest", type=Path)
    parser.add_argument("ibtracs_csv", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--sequence-length", type=int, default=4)
    parser.add_argument("--cadence-hours", type=int, default=3)
    parser.add_argument("--tolerance-minutes", type=int, default=90)
    parser.add_argument("--forecast-hours", type=int, default=24)
    args = parser.parse_args()

    fused = read_jsonl(args.fused_manifest)
    tracks = load_ibtracs_csv(args.ibtracs_csv, target_basin="NI")
    records = build_labeled_sequences(
        fused,
        tracks,
        sequence_length=args.sequence_length,
        cadence_hours=args.cadence_hours,
        tolerance_minutes=args.tolerance_minutes,
        forecast_hours=args.forecast_hours,
    )
    write_jsonl(records, args.output)
    print(f"sequence_samples={len(records)}")


if __name__ == "__main__":
    main()
