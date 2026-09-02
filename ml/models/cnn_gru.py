"""CNN + GRU temporal multi-task cyclone model."""

from __future__ import annotations

import torch
from torch import nn


class CNNFrameEncoder(nn.Module):
    def __init__(self, channels: int = 4, embedding_dim: int = 128) -> None:
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(channels, 32, 3, padding=1),
            nn.BatchNorm2d(32), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1),
            nn.BatchNorm2d(64), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(64, 128, 3, padding=1),
            nn.BatchNorm2d(128), nn.ReLU(),
            nn.AdaptiveAvgPool2d(1),
        )
        self.projection = nn.Sequential(
            nn.Flatten(),
            nn.Linear(128, embedding_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
        )

    def forward(self, frames: torch.Tensor) -> torch.Tensor:
        return self.projection(self.features(frames))


class CNNGRUMultiTaskNet(nn.Module):
    """Encode each satellite frame, model evolution with a GRU, then predict."""

    def __init__(
        self,
        channels: int = 4,
        embedding_dim: int = 128,
        hidden_dim: int = 128,
        num_classes: int = 7,
        forecast_steps: int = 1,
    ) -> None:
        super().__init__()
        self.forecast_steps = forecast_steps
        self.encoder = CNNFrameEncoder(channels, embedding_dim)
        self.gru = nn.GRU(embedding_dim, hidden_dim, batch_first=True)
        self.detection_head = nn.Linear(hidden_dim, 1)
        self.class_head = nn.Linear(hidden_dim, num_classes)
        self.intensity_head = nn.Linear(hidden_dim, 1)
        self.track_head = nn.Linear(hidden_dim, forecast_steps * 2)

    def forward(self, sequence: torch.Tensor) -> dict[str, torch.Tensor]:
        if sequence.ndim != 5:
            raise ValueError("sequence must have shape [B, T, C, H, W]")
        batch, steps, channels, height, width = sequence.shape
        encoded = self.encoder(sequence.reshape(batch * steps, channels, height, width))
        encoded = encoded.reshape(batch, steps, -1)
        temporal, _ = self.gru(encoded)
        state = temporal[:, -1]
        return {
            "detection_logits": self.detection_head(state),
            "class_logits": self.class_head(state),
            "intensity": self.intensity_head(state),
            "track": self.track_head(state).reshape(batch, self.forecast_steps, 2),
        }
