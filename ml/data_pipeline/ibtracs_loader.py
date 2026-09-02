"""IBTrACS CSV loader for the CycloneAI training pipeline.

The loader intentionally normalizes only the fields needed by the first
prototype. It accepts the common IBTrACS CSV layout and keeps source values
available for later auditing.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class TrackRecord:
    storm_id: str
    name: str
    basin: str
    timestamp: datetime
    latitude: float
    longitude: float
    wind_knots: float | None
    pressure_hpa: float | None


def _clean(value: str | None) -> str:
    return (value or "").strip()


def _float(value: str | None) -> float | None:
    value = _clean(value)
    if not value or value in {"-999", "-999.0", "NA", "N/A"}:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _parse_time(value: str) -> datetime:
    value = _clean(value)
    formats = ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S")
    for fmt in formats:
        try:
            return datetime.strptime(value, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    raise ValueError(f"Unsupported ISO_TIME value: {value!r}")


def _first_column(row: dict[str, str], *names: str) -> str:
    for name in names:
        if name in row and _clean(row[name]):
            return row[name]
    return ""


def load_ibtracs_csv(path: str | Path, target_basin: str = "NI") -> list[TrackRecord]:
    """Load and filter an IBTrACS CSV by basin.

    IBTrACS CSV files may contain a units row after the header. Rows without a
    usable timestamp/position are skipped rather than silently converted.
    """
    records: list[TrackRecord] = []
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError("IBTrACS CSV has no header")

        required = {"SID", "BASIN", "ISO_TIME", "LAT", "LON"}
        missing = required - set(reader.fieldnames)
        if missing:
            raise ValueError(f"IBTrACS CSV missing columns: {sorted(missing)}")

        for row in reader:
            if _clean(row.get("BASIN")) != target_basin:
                continue
            try:
                timestamp = _parse_time(row.get("ISO_TIME", ""))
                latitude = _float(row.get("LAT"))
                longitude = _float(row.get("LON"))
            except ValueError:
                continue
            if latitude is None or longitude is None:
                continue
            if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
                continue

            records.append(
                TrackRecord(
                    storm_id=_clean(row.get("SID")),
                    name=_clean(row.get("NAME")),
                    basin=_clean(row.get("BASIN")),
                    timestamp=timestamp,
                    latitude=latitude,
                    longitude=longitude,
                    wind_knots=_float(_first_column(row, "USA_WIND", "WMO_WIND")),
                    pressure_hpa=_float(_first_column(row, "USA_PRES", "WMO_PRES")),
                )
            )

    return records
