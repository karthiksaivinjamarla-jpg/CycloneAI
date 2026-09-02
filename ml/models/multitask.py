"""Baseline multi-task CNN for CycloneAI.

This is intentionally a small, trainable baseline. It provides a stable model
contract for the team before experimenting with larger encoders or temporal
transformers.
"""

from __future__ import annotations

from typing import Any


def build_model(
    channels: int = 4,
    num_classes: int = 7,
    forecast_steps: int = 1,
) -> Any:
    """Build a CNN with detection, class, intensity and track heads.

    The first baseline predicts one configurable future point. A later temporal
    model can set forecast_steps=4 for +6/+12/+24/+48 hour forecasts.
    """
    try:
        import torch
        from torch import nn
    except ImportError as exc:
        raise RuntimeError("Install PyTorch to build the CycloneAI model") from exc

    class CycloneMultiTaskNet(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.encoder = nn.Sequential(
                nn.Conv2d(channels, 32, 3, padding=1),
                nn.BatchNorm2d(32),
                nn.ReLU(),
                nn.MaxPool2d(2),
                nn.Conv2d(32, 64, 3, padding=1),
                nn.BatchNorm2d(64),
                nn.ReLU(),
                nn.MaxPool2d(2),
                nn.Conv2d(64, 128, 3, padding=1),
                nn.BatchNorm2d(128),
                nn.ReLU(),
                nn.AdaptiveAvgPool2d(1),
            )
            self.shared = nn.Sequential(nn.Flatten(), nn.Linear(128, 128), nn.ReLU(), nn.Dropout(0.2))
            self.detection_head = nn.Linear(128, 1)
            self.class_head = nn.Linear(128, num_classes)
            self.intensity_head = nn.Linear(128, 1)
            self.track_head = nn.Linear(128, forecast_steps * 2)
            self.forecast_steps = forecast_steps

        def forward(self, x: torch.Tensor) -> dict[str, torch.Tensor]:
            features = self.shared(self.encoder(x))
            return {
                "detection_logits": self.detection_head(features),
                "class_logits": self.class_head(features),
                "intensity": self.intensity_head(features),
                "track": self.track_head(features).view(-1, self.forecast_steps, 2),
            }

    return CycloneMultiTaskNet()
