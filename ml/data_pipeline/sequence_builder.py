"""Build fixed-length multi-channel temporal sequences from fused frames."""

from __future__ import annotations

from datetime import datetime, timedelta


def _parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed.replace(tzinfo=None) if parsed.tzinfo else parsed


def build_sequences(
    frames: list[dict[str, object]],
    sequence_length: int = 4,
    cadence_hours: int = 3,
    tolerance_minutes: int = 90,
) -> list[dict[str, object]]:
    """Create sequences ending at each eligible frame.

    Frames must already be fused by storm and timestamp. Each sequence contains
    the current frame plus preceding observations at the requested cadence.
    Missing cadence slots invalidate the sequence rather than silently reusing
    an unrelated observation.
    """
    grouped: dict[str, list[dict[str, object]]] = {}
    for frame in frames:
        grouped.setdefault(str(frame["storm_id"]), []).append(frame)

    tolerance = timedelta(minutes=tolerance_minutes)
    step = timedelta(hours=cadence_hours)
    output: list[dict[str, object]] = []

    for storm_id, rows in grouped.items():
        rows.sort(key=lambda row: _parse_time(str(row["timestamp"])))
        by_time = {_parse_time(str(row["timestamp"])): row for row in rows}
        for current in rows:
            end = _parse_time(str(current["timestamp"]))
            selected: list[dict[str, object]] = []
            valid = True
            for offset in range(sequence_length - 1, -1, -1):
                wanted = end - offset * step
                candidates = [t for t in by_time if abs(t - wanted) <= tolerance]
                if not candidates:
                    valid = False
                    break
                selected.append(by_time[min(candidates, key=lambda t: abs(t - wanted))])
            if not valid:
                continue
            output.append({
                "storm_id": storm_id,
                "timestamp": current["timestamp"],
                "frames": selected,
                "sequence_length": sequence_length,
                "cadence_hours": cadence_hours,
            })
    return output
