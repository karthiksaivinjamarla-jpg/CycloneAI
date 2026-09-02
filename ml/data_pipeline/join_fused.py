"""Join fused satellite frames with IBTrACS labels and 24-hour targets."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path

from ml.data_pipeline.ibtracs_loader import load_ibtracs_csv
from ml.data_pipeline.labels import classify_wind, track_offsets


def read_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def parse_time(value: object) -> datetime:
    text = str(value).replace("Z", "+00:00")
    parsed = datetime.fromisoformat(text)
    return parsed.replace(tzinfo=None) if parsed.tzinfo else parsed


def build_labeled_manifest(
    fused_frames: list[dict[str, object]],
    tracks: list[object],
    tolerance_minutes: int = 90,
    forecast_hours: int = 24,
) -> list[dict[str, object]]:
    by_storm: dict[str, list[object]] = {}
    for track in tracks:
        by_storm.setdefault(track.storm_id, []).append(track)
    for rows in by_storm.values():
        rows.sort(key=lambda row: row.timestamp)

    output: list[dict[str, object]] = []
    tolerance = timedelta(minutes=tolerance_minutes)
    target_delta = timedelta(hours=forecast_hours)

    for frame in fused_frames:
        storm_id = str(frame["storm_id"])
        if storm_id not in by_storm:
            continue
        timestamp = parse_time(frame["timestamp"])
        rows = by_storm[storm_id]
        current = min(rows, key=lambda row: abs(row.timestamp - timestamp))
        if abs(current.timestamp - timestamp) > tolerance or current.wind_knots is None:
            continue
        target_time = current.timestamp + target_delta
        future = min(rows, key=lambda row: abs(row.timestamp - target_time))
        if abs(future.timestamp - target_time) > tolerance:
            continue

        class_idx, _ = classify_wind(current.wind_knots)
        output.append({
            "storm_id": storm_id,
            "timestamp": frame["timestamp"],
            "image_paths": frame["image_paths"],
            "available_channels": frame.get("available_channels", []),
            "detected": True,
            "class_index": class_idx,
            "wind_knots": float(current.wind_knots),
            "track_offsets": [track_offsets(current.latitude, current.longitude, future.latitude, future.longitude)],
            "target_timestamp": future.timestamp.isoformat(),
        })
    return output


def write_jsonl(records: list[dict[str, object]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Join fused satellite frames with IBTrACS labels")
    parser.add_argument("fused_manifest", type=Path)
    parser.add_argument("ibtracs_csv", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--tolerance-minutes", type=int, default=90)
    parser.add_argument("--forecast-hours", type=int, default=24)
    args = parser.parse_args()

    fused = read_jsonl(args.fused_manifest)
    tracks = load_ibtracs_csv(args.ibtracs_csv, target_basin="NI")
    records = build_labeled_manifest(fused, tracks, args.tolerance_minutes, args.forecast_hours)
    write_jsonl(records, args.output)
    print(f"labeled_samples={len(records)}")


if __name__ == "__main__":
    main()
