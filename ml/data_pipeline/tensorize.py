from __future__ import annotations

import numpy as np

from .satellite_reader import read_satellite_array

CHANNEL_ORDER = ("IR", "WV", "VIS", "MW")


def resize_frame(frame: np.ndarray, size: int = 201) -> np.ndarray:
    """Resize a 2-D frame using OpenCV when available."""
    if frame.ndim != 2:
        raise ValueError(f"Expected 2-D frame, got {frame.shape}")
    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError("Install opencv-python for satellite resizing") from exc
    return cv2.resize(frame, (size, size), interpolation=cv2.INTER_AREA).astype(np.float32)


def robust_normalize(frame: np.ndarray) -> np.ndarray:
    """Normalize a channel using robust percentiles, then map to roughly 0..1."""
    finite = frame[np.isfinite(frame)]
    if finite.size == 0:
        return np.zeros_like(frame, dtype=np.float32)
    low, high = np.percentile(finite, [1, 99])
    if high <= low:
        return np.zeros_like(frame, dtype=np.float32)
    clipped = np.clip(frame, low, high)
    return ((clipped - low) / (high - low)).astype(np.float32)


def load_multichannel_tensor(
    channel_paths: dict[str, str],
    size: int = 201,
    require_channels: bool = False,
) -> np.ndarray:
    """Load channels into a CHW tensor in fixed IR/WV/VIS/MW order."""
    missing = [channel for channel in CHANNEL_ORDER if channel not in channel_paths]
    if require_channels and missing:
        raise ValueError(f"Missing required satellite channels: {missing}")

    tensors: list[np.ndarray] = []
    for channel in CHANNEL_ORDER:
        path = channel_paths.get(channel)
        if path is None:
            tensors.append(np.zeros((size, size), dtype=np.float32))
            continue
        frame = read_satellite_array(path, channel)
        tensors.append(robust_normalize(resize_frame(frame, size)))

    return np.stack(tensors, axis=0).astype(np.float32, copy=False)
