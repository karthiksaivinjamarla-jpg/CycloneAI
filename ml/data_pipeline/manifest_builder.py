"""Build a JSONL training manifest from joined satellite/track samples.

The builder intentionally writes references to raw files rather than copying
raw satellite archives into Git.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .labels import classify_wind, track_offsets
from .sample_builder import ForecastSample


def build_manifest(samples: list[ForecastSample], satellite_index: dict[tuple[str, str], dict[str, str]], winds: dict[tuple[str, str], float]) -> list[dict]:
    records: list[dict] = []
    for sample in samples:
        key = (sample.storm_id, sample.input_times[-1])
        wind = winds.get(key)
        if wind is None:
            continue
        class_index, class_label = classify_wind(wind)
        paths = satellite_index.get(key, {})
        records.append({
            "storm_id": sample.storm_id,
            "timestamp": sample.input_times[-1],
            "input_times": list(sample.input_times),
            "image_paths": paths,
            "detected": True,
            "class_index": class_index,
            "class_label": class_label,
            "wind_knots": wind,
            "track_offsets": [track_offsets(sample.center_latitude, sample.center_longitude, sample.target_latitude, sample.target_longitude)],
            "forecast_hours": sample.forecast_hours,
        })
    return records


def write_jsonl(records: list[dict], output: str | Path) -> None:
    Path(output).write_text("\n".join(json.dumps(r) for r in records) + ("\n" if records else ""), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit("Use build_manifest() from a dataset-specific ingestion script; raw dataset formats are intentionally not assumed here.")
