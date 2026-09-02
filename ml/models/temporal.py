"""Temporal wrapper around the baseline CNN encoder."""

from __future__ import annotations

from typing import Any


class TemporalMultiTaskNet:
    """Specification wrapper for sequence inference.

    The first experiment keeps the existing CNN heads unchanged. This wrapper
    documents the tensor contract for the next trained temporal model:
    [batch, sequence, channels, height, width].
    """

    input_shape = "[B, T, C, H, W]"
    output_shape = "same multi-task heads as CycloneMultiTaskNet"

    def __init__(self, frame_model: Any) -> None:
        self.frame_model = frame_model

    def encode_sequence(self, sequence: Any) -> Any:
        if getattr(sequence, "ndim", None) != 5:
            raise ValueError("sequence must have shape [B, T, C, H, W]")
        batch, steps, channels, height, width = sequence.shape
        flattened = sequence.reshape(batch * steps, channels, height, width)
        return self.frame_model(flattened)
