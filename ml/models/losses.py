from __future__ import annotations

from typing import Any


def multitask_loss(outputs: dict[str, Any], targets: dict[str, Any]) -> Any:
    """Weighted baseline loss for the four model objectives."""
    import torch.nn.functional as F

    detection = F.binary_cross_entropy_with_logits(
        outputs["detection_logits"].squeeze(-1), targets["detected"].float()
    )
    classification = F.cross_entropy(outputs["class_logits"], targets["class_index"].long())
    intensity = F.smooth_l1_loss(outputs["intensity"].squeeze(-1), targets["wind_knots"].float())
    track = F.smooth_l1_loss(outputs["track"], targets["track_offsets"].float())

    return detection + classification + 0.25 * intensity + track
