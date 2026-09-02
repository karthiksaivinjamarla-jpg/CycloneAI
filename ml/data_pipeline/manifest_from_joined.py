"""Turn joined satellite/track observations into training JSONL.

This is deliberately a local ingestion utility: raw datasets stay outside the
repository, while the generated JSONL contains file references and labels.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .ibtracs_loader import load_ibtracs_csv
from .join import join_nearest_satellite
from .labels import classify_wind, track_offsets
from .sample_builder import build_samples
from .satellite_manifest import SatelliteFrame


def read_satellite_manifest(path: str | Path) -> list[SatelliteFrame]:
    frames: list[SatelliteFrame] = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        frames.append(
            SatelliteFrame(
                storm_id=item["storm_id"],
                timestamp=__import__("datetime").datetime.fromisoformat(item["timestamp"].replace("Z", "+00:00")),
                source=item.get("source", "unknown"),
                channel=item["channel"],
                path=item["path"],
                latitude=item.get("latitude"),
                longitude=item.get("longitude"),
            )
        )
    return frames


def build_training_manifest(ibtracs_csv: str | Path, satellite_jsonl: str | Path, output: str | Path, forecast_hours: int = 24) -> int:
    records = load_ibtracs_csv(ibtracs_csv, target_basin="NI")
    observations = records
    frames = read_satellite_manifest(satellite_jsonl)
    joined = join_nearest_satellite(observations, frames)

    samples = build_samples(observations, input_steps=1, forecast_hours=forecast_hours)
    joined_by_key = {(x.storm_id, x.timestamp): x for x in joined}
    track_by_key = {(x.storm_id, x.timestamp): x for x in observations}

    rows: list[dict] = []
    for sample in samples:
        key = (sample.storm_id, sample.input_times[-1])
        current = track_by_key.get(key)
        joined_item = joined_by_key.get(key)
        if current is None or joined_item is None or not joined_item.channels:
            continue
        if current.wind_knots is None:
            continue

        class_index, class_label = classify_wind(current.wind_knots)
        rows.append({
            "storm_id": sample.storm_id,
            "timestamp": sample.input_times[-1],
            "input_times": list(sample.input_times),
            "image_paths": joined_item.channels,
            "detected": True,
            "class_index": class_index,
            "class_label": class_label,
            "wind_knots": current.wind_knots,
            "track_offsets": [track_offsets(sample.center_latitude, sample.center_longitude, sample.target_latitude, sample.target_longitude)],
            "forecast_hours": forecast_hours,
        })

    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(json.dumps(row) for row in rows) + ("\n" if rows else ""), encoding="utf-8")
    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("ibtracs_csv")
    parser.add_argument("satellite_jsonl")
    parser.add_argument("output")
    parser.add_argument("--forecast-hours", type=int, default=24)
    args = parser.parse_args()
    print(build_training_manifest(args.ibtracs_csv, args.satellite_jsonl, args.output, args.forecast_hours))


if __name__ == "__main__":
    main()
