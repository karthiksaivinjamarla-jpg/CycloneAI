"""Load a trained CNN-GRU checkpoint and run a single prediction."""
from __future__ import annotations

from pathlib import Path
from typing import Sequence

import numpy as np
import torch

from ml.models.cnn_gru import CNNGRUMultiTaskNet

IMD_CLASSES = (
    "Depression",
    "Deep Depression",
    "Cyclonic Storm",
    "Severe Cyclonic Storm",
    "Very Severe Cyclonic Storm",
    "Extremely Severe Cyclonic Storm",
    "Super Cyclonic Storm",
)


class CyclonePredictor:
    """Versioned inference wrapper for the trained CNN-GRU model."""

    def __init__(self, checkpoint_path: str | Path, device: str | None = None) -> None:
        self.device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
        checkpoint = torch.load(checkpoint_path, map_location=self.device, weights_only=False)
        self.model = CNNGRUMultiTaskNet(
            channels=len(checkpoint.get("channels", ["IR", "WV", "VIS", "MW"])),
            forecast_steps=1,
        ).to(self.device)
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.model.eval()
        self.model_version = checkpoint.get("model_version", "unknown")

    @torch.inference_mode()
    def predict(self, sequence: np.ndarray) -> dict[str, object]:
        if sequence.ndim != 4:
            raise ValueError("sequence must have shape [T, C, H, W]")
        tensor = torch.from_numpy(sequence.astype(np.float32)).unsqueeze(0).to(self.device)
        outputs = self.model(tensor)

        detection_probability = torch.sigmoid(outputs["detection_logits"])[0, 0].item()
        class_probabilities = torch.softmax(outputs["class_logits"], dim=-1)[0]
        class_index = int(torch.argmax(class_probabilities).item())
        wind_knots = float(outputs["intensity"][0, 0].item())
        track_offset = outputs["track"][0, 0].detach().cpu().tolist()

        return {
            "cyclone_detected": detection_probability >= 0.5,
            "detection_confidence": detection_probability,
            "classification": {
                "label": IMD_CLASSES[class_index],
                "confidence": float(class_probabilities[class_index].item()),
            },
            "intensity": {"wind_knots": wind_knots},
            "track_offset": {"latitude": float(track_offset[0]), "longitude": float(track_offset[1])},
            "model_version": self.model_version,
        }
