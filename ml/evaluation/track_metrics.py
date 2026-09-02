"""Geographically correct cyclone track evaluation utilities."""
from __future__ import annotations

from math import asin, cos, radians, sin, sqrt
from typing import Sequence

EARTH_RADIUS_KM = 6371.0088


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_KM * asin(sqrt(min(1.0, a)))


def offsets_to_coordinates(
    origins: Sequence[tuple[float, float]],
    offsets: Sequence[tuple[float, float]],
) -> list[tuple[float, float]]:
    if len(origins) != len(offsets):
        raise ValueError("origins and offsets must have the same length")
    return [(lat + dlat, lon + dlon) for (lat, lon), (dlat, dlon) in zip(origins, offsets)]


def mean_track_error_km(
    origins: Sequence[tuple[float, float]],
    predicted_offsets: Sequence[tuple[float, float]],
    actual_offsets: Sequence[tuple[float, float]],
) -> float:
    if not origins:
        raise ValueError("at least one track sample is required")
    predicted = offsets_to_coordinates(origins, predicted_offsets)
    actual = offsets_to_coordinates(origins, actual_offsets)
    errors = [haversine_km(p_lat, p_lon, a_lat, a_lon) for (p_lat, p_lon), (a_lat, a_lon) in zip(predicted, actual)]
    return sum(errors) / len(errors)
