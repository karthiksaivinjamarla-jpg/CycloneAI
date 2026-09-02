from __future__ import annotations

import torch

from ml.models.cnn_gru import CNNGRUMultiTaskNet


def test_cnn_gru_output_shapes():
    model = CNNGRUMultiTaskNet(num_classes=7, forecast_steps=2)
    x = torch.randn(2, 4, 4, 64, 64)
    outputs = model(x)
    assert outputs["detection_logits"].shape == (2, 1)
    assert outputs["class_logits"].shape == (2, 7)
    assert outputs["intensity"].shape == (2, 1)
    assert outputs["track"].shape == (2, 2, 2)


def test_cnn_gru_rejects_frame_input():
    model = CNNGRUMultiTaskNet()
    try:
        model(torch.randn(2, 4, 64, 64))
    except ValueError as exc:
        assert "[B, T, C, H, W]" in str(exc)
    else:
        raise AssertionError("expected a ValueError for non-sequence input")
