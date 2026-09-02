from __future__ import annotations

from typing import Any


def multitask_loss(outputs: dict[str, Any], targets: dict[str, Any]) -> Any:
    """Weighted multi-task loss with positive-only regression/classification terms.

    Detection is learned from every sample. Cyclone class, intensity, and track
    targets are meaningful only when a cyclone is detected, so negative samples
    are masked out of those objectives.
    """
    import torch
    import torch.nn.functional as F

    detected = targets["detected"].float().view(-1)
    detection = F.binary_cross_entropy_with_logits(
        outputs["detection_logits"].view(-1), detected
    )

    positive = detected > 0.5
    if positive.any():
        classification = F.cross_entropy(
            outputs["class_logits"][positive], targets["class_index"].long()[positive]
        )
        intensity = F.smooth_l1_loss(
            outputs["intensity"].view(-1)[positive], targets["wind_knots"].float().view(-1)[positive]
        )
        track = F.smooth_l1_loss(
            outputs["track"][positive], targets["track_offsets"].float()[positive]
        )
    else:
        zero = torch.zeros((), device=detected.device, dtype=detected.dtype)
        classification = zero
        intensity = zero
        track = zero

    return detection + classification + 0.25 * intensity + track
