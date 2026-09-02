"""Validation helpers for the CycloneAI multi-task baseline."""

from __future__ import annotations

from typing import Any

from ml.evaluation.metrics import (
    binary_classification_metrics,
    macro_f1,
    mean_absolute_error,
    root_mean_squared_error,
    track_error_km,
)


def evaluate(model: Any, loader: Any, device: Any) -> dict[str, float]:
    import torch

    model.eval()
    detection_probabilities: list[float] = []
    detection_targets: list[int] = []
    class_predictions: list[int] = []
    class_targets: list[int] = []
    wind_predictions: list[float] = []
    wind_targets: list[float] = []
    track_predictions: list[tuple[float, float]] = []
    track_targets: list[tuple[float, float]] = []

    with torch.no_grad():
        for batch in loader:
            outputs = model(batch["images"].to(device))
            targets = batch["targets"]
            detection_probabilities.extend(torch.sigmoid(outputs["detection_logits"]).squeeze(1).cpu().tolist())
            detection_targets.extend(targets["detected"].int().tolist())
            class_predictions.extend(outputs["class_logits"].argmax(dim=1).cpu().tolist())
            class_targets.extend(targets["class_index"].cpu().tolist())
            wind_predictions.extend(outputs["intensity"].squeeze(1).cpu().tolist())
            wind_targets.extend(targets["wind_knots"].cpu().tolist())
            predicted = outputs["track"][:, 0, :].cpu().tolist()
            actual = targets["track_offsets"][:, 0, :].cpu().tolist()
            track_predictions.extend((p[0], p[1]) for p in predicted)
            track_targets.extend((a[0], a[1]) for a in actual)

    result: dict[str, float] = {}
    if detection_targets and len(set(detection_targets)) > 1:
        detection = binary_classification_metrics(
            [int(p >= 0.5) for p in detection_probabilities], detection_targets
        )
        result.update({f"detection_{k}": v for k, v in detection.items()})
    if class_targets:
        result["classification_macro_f1"] = macro_f1(class_predictions, class_targets, num_classes=7)
    if wind_targets:
        result["intensity_mae_knots"] = mean_absolute_error(wind_predictions, wind_targets)
        result["intensity_rmse_knots"] = root_mean_squared_error(wind_predictions, wind_targets)
    if track_targets:
        result["track_error_km"] = track_error_km(track_predictions, track_targets)
    return result
