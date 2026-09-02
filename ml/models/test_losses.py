"""Sanity checks for masked multi-task loss."""

from __future__ import annotations

import torch

from ml.models.losses import multitask_loss


def _outputs(batch: int = 2):
    return {
        "detection_logits": torch.zeros(batch, 1, requires_grad=True),
        "class_logits": torch.zeros(batch, 7, requires_grad=True),
        "intensity": torch.zeros(batch, 1, requires_grad=True),
        "track": torch.zeros(batch, 1, 2, requires_grad=True),
    }


def test_negative_samples_only_contribute_detection_loss():
    outputs = _outputs()
    targets = {
        "detected": torch.tensor([0.0, 0.0]),
        "class_index": torch.tensor([99, 99]),
        "wind_knots": torch.tensor([999.0, 999.0]),
        "track_offsets": torch.tensor([[[999.0, 999.0]], [[999.0, 999.0]]]),
    }
    loss = multitask_loss(outputs, targets)
    expected = torch.tensor(0.69314718)
    assert torch.isclose(loss.detach(), expected, atol=1e-5)


def test_positive_and_negative_samples_are_supported():
    outputs = _outputs()
    targets = {
        "detected": torch.tensor([1.0, 0.0]),
        "class_index": torch.tensor([2, 99]),
        "wind_knots": torch.tensor([40.0, 999.0]),
        "track_offsets": torch.tensor([[[1.0, 2.0]], [[999.0, 999.0]]]),
    }
    loss = multitask_loss(outputs, targets)
    loss.backward()
    assert torch.isfinite(loss)
