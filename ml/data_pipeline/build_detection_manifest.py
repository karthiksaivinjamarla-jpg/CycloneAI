"""Build a balanced detection manifest from positive and negative frames.

Input satellite JSONL uses one frame per line with storm_id/timestamp/channel/path.
A frame is positive when its storm_id is present in the cyclone track set.
Negative frames are sampled from all other storm IDs. Sampling is performed by
storm ID so one source sequence cannot leak across the split later.
"""

from __future__ import annotations

import argparse
import json
import random
from collections import defaultdict
from pathlib import Path


def read_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def build_detection_records(
    frames: list[dict[str, object]],
    cyclone_storm_ids: set[str],
    negative_ratio: float = 1.0,
    seed: int = 42,
) -> list[dict[str, object]]:
    rng = random.Random(seed)
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for frame in frames:
        grouped[str(frame["storm_id"])].append(frame)

    positive = [frame for storm_id, rows in grouped.items() if storm_id in cyclone_storm_ids for frame in rows]
    negative_storms = [storm_id for storm_id in grouped if storm_id not in cyclone_storm_ids]
    rng.shuffle(negative_storms)
    target_negative = min(len(negative_storms), max(1, round(len(cyclone_storm_ids) * negative_ratio)))
    selected_negative_storms = set(negative_storms[:target_negative])
    negative = [frame for storm_id in selected_negative_storms for frame in grouped[storm_id]]

    records: list[dict[str, object]] = []
    for frame in positive:
        records.append({
            "storm_id": frame["storm_id"],
            "timestamp": frame["timestamp"],
            "image_paths": {frame["channel"]: frame["path"]},
            "detected": True,
            "class_index": 0,
            "wind_knots": 0.0,
            "track_offsets": [[0.0, 0.0]],
        })
    for frame in negative:
        records.append({
            "storm_id": frame["storm_id"],
            "timestamp": frame["timestamp"],
            "image_paths": {frame["channel"]: frame["path"]},
            "detected": False,
            "class_index": 0,
            "wind_knots": 0.0,
            "track_offsets": [[0.0, 0.0]],
        })
    rng.shuffle(records)
    return records


def write_jsonl(records: list[dict[str, object]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("satellite_manifest", type=Path)
    parser.add_argument("cyclone_ids", type=Path, help="JSON file containing a list of cyclone storm IDs")
    parser.add_argument("output", type=Path)
    parser.add_argument("--negative-ratio", type=float, default=1.0)
    args = parser.parse_args()

    frames = read_jsonl(args.satellite_manifest)
    cyclone_ids = set(json.loads(args.cyclone_ids.read_text(encoding="utf-8")))
    records = build_detection_records(frames, cyclone_ids, args.negative_ratio)
    write_jsonl(records, args.output)
    positives = sum(bool(record["detected"]) for record in records)
    print(f"records={len(records)} positives={positives} negatives={len(records)-positives}")


if __name__ == "__main__":
    main()
