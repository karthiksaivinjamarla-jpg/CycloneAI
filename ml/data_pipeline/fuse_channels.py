"""Fuse satellite channel rows into one multi-channel JSONL frame manifest."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from ml.data_pipeline.satellite_manifest import SUPPORTED_CHANNELS


def read_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def fuse_frames(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], dict[str, str]] = defaultdict(dict)
    for row in rows:
        storm_id = str(row["storm_id"])
        timestamp = str(row["timestamp"])
        channel = str(row["channel"])
        if channel not in SUPPORTED_CHANNELS:
            continue
        grouped[(storm_id, timestamp)][channel] = str(row["path"])

    result = []
    for (storm_id, timestamp), channels in sorted(grouped.items()):
        result.append({
            "storm_id": storm_id,
            "timestamp": timestamp,
            "image_paths": {channel: channels[channel] for channel in SUPPORTED_CHANNELS if channel in channels},
            "available_channels": [channel for channel in SUPPORTED_CHANNELS if channel in channels],
        })
    return result


def write_jsonl(records: list[dict[str, object]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Fuse IR/WV/VIS/MW rows by storm and timestamp")
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    records = fuse_frames(read_jsonl(args.input))
    write_jsonl(records, args.output)
    complete = sum(len(record["available_channels"]) == 4 for record in records)
    print(f"fused_frames={len(records)} complete_4ch={complete}")


if __name__ == "__main__":
    main()
