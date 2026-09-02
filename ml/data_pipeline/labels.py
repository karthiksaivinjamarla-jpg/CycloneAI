"""IMD-style labels derived from maximum sustained wind in knots."""

from __future__ import annotations

IMD_WIND_CLASSES = (
    (17, 27, "Depression"),
    (28, 33, "Deep Depression"),
    (34, 47, "Cyclonic Storm"),
    (48, 63, "Severe Cyclonic Storm"),
    (64, 89, "Very Severe Cyclonic Storm"),
    (90, 119, "Extremely Severe Cyclonic Storm"),
    (120, float("inf"), "Super Cyclonic Storm"),
)


def classify_wind(wind_knots: float) -> tuple[int, str]:
    if wind_knots < 17:
        raise ValueError("Wind below 17 kt is outside the cyclone-class baseline")
    for index, (low, high, label) in enumerate(IMD_WIND_CLASSES):
        if low <= wind_knots <= high:
            return index, label
    raise ValueError(f"Unsupported wind speed: {wind_knots}")


def track_offsets(center_lat: float, center_lon: float, target_lat: float, target_lon: float) -> list[float]:
    """Return a simple relative latitude/longitude target."""
    return [target_lat - center_lat, target_lon - center_lon]
