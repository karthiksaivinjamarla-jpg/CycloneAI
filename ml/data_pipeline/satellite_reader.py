"""Lightweight satellite array reader.

Supports NetCDF/HDF-like files through xarray when installed. Raw satellite
archives are intentionally kept outside Git; this module operates on local
paths supplied by a manifest.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np


DEFAULT_VARIABLES = {
    "IR": ("IR", "ir", "infrared", "brightness_temperature"),
    "WV": ("WV", "wv", "water_vapor"),
    "VIS": ("VIS", "vis", "visible", "reflectance"),
    "MW": ("MW", "mw", "microwave"),
}


def _select_variable(dataset: Any, channel: str) -> Any:
    candidates = DEFAULT_VARIABLES[channel]
    for name in candidates:
        if name in dataset.data_vars:
            return dataset[name]
    raise KeyError(
        f"No variable found for {channel}. Available variables: {list(dataset.data_vars)}"
    )


def read_satellite_array(path: str | Path, channel: str) -> np.ndarray:
    """Read one channel and return a finite float32 array.

    The reader deliberately does not assume a particular satellite provider's
    variable name. Dataset-specific aliases are centralized above and can be
    extended without changing the training code.
    """
    channel = channel.upper()
    if channel not in DEFAULT_VARIABLES:
        raise ValueError(f"Unsupported channel: {channel}")

    try:
        import xarray as xr
    except ImportError as exc:
        raise RuntimeError("Install xarray and a NetCDF/HDF backend to read satellite files") from exc

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)

    with xr.open_dataset(path) as dataset:
        values = np.asarray(_select_variable(dataset, channel).values, dtype=np.float32)

    if values.ndim < 2:
        raise ValueError(f"Satellite array must be at least 2-D, got shape {values.shape}")

    # Remove singleton dimensions while preserving the final spatial axes.
    values = np.squeeze(values)
    if values.ndim != 2:
        raise ValueError(f"Expected a single 2-D satellite frame, got shape {values.shape}")

    values = np.nan_to_num(values, nan=0.0, posinf=0.0, neginf=0.0)
    return values.astype(np.float32, copy=False)
