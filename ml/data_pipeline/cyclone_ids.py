"""Extract North Indian Ocean cyclone IDs from an IBTrACS CSV."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ml.data_pipeline.ibtracs_loader import load_ibtracs_csv


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("ibtracs_csv", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    records = load_ibtracs_csv(args.ibtracs_csv, target_basin="NI")
    storm_ids = sorted({record.storm_id for record in records})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(storm_ids, indent=2) + "\n", encoding="utf-8")
    print(f"storm_ids={len(storm_ids)} output={args.output}")


if __name__ == "__main__":
    main()
