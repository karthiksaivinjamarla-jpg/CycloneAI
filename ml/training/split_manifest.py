"""Create storm-level train/validation/test manifests without leakage."""

from __future__ import annotations

import argparse
import json
import random
from collections import defaultdict
from pathlib import Path


def split_records(records: list[dict], seed: int = 42, train_ratio: float = 0.7, val_ratio: float = 0.15):
    groups: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        storm_id = record.get("storm_id")
        if not storm_id:
            raise ValueError("Every record must contain storm_id")
        groups[storm_id].append(record)

    storm_ids = list(groups)
    random.Random(seed).shuffle(storm_ids)
    n = len(storm_ids)
    train_end = int(n * train_ratio)
    val_end = train_end + int(n * val_ratio)
    train_ids = set(storm_ids[:train_end])
    val_ids = set(storm_ids[train_end:val_end])
    test_ids = set(storm_ids[val_end:])

    return (
        [r for r in records if r["storm_id"] in train_ids],
        [r for r in records if r["storm_id"] in val_ids],
        [r for r in records if r["storm_id"] in test_ids],
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()

    records = [json.loads(line) for line in args.manifest.read_text(encoding="utf-8").splitlines() if line.strip()]
    train, validation, test = split_records(records)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    for name, rows in (("train", train), ("validation", validation), ("test", test)):
        output = args.output_dir / f"{name}.jsonl"
        output.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
        print(f"{name}: {len(rows)} samples")


if __name__ == "__main__":
    main()
