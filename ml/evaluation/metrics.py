from __future__ import annotations

import math
from typing import Sequence


def mean_absolute_error(predicted: Sequence[float], actual: Sequence[float]) -> float:
    if len(predicted) != len(actual) or not predicted:
        raise ValueError("predicted and actual must have the same non-empty length")
    return sum(abs(p - a) for p, a in zip(predicted, actual)) / len(predicted)


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * radius * math.asin(math.sqrt(min(1.0, a)))


def track_error_km(predicted: Sequence[tuple[float, float]], actual: Sequence[tuple[float, float]]) -> float:
    if len(predicted) != len(actual) or not predicted:
        raise ValueError("predicted and actual tracks must have the same non-empty length")
    distances = [haversine_km(a, b, c, d) for (a, b), (c, d) in zip(predicted, actual)]
    return sum(distances) / len(distances)
