"""Model inference service used by the FastAPI layer."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import numpy as np

from ml.inference.predict import CyclonePredictor


class ModelService:
    def __init__(self) -> None:
        checkpoint = os.getenv("CYCLONE_MODEL_CHECKPOINT")
        self.predictor = CyclonePredictor(checkpoint) if checkpoint and Path(checkpoint).exists() else None

    @property
    def available(self) -> bool:
        return self.predictor is not None

    def predict(self, sequence: np.ndarray) -> dict[str, Any]:
        if self.predictor is None:
            raise RuntimeError("trained model checkpoint is not configured")
        return self.predictor.predict(sequence)


model_service = ModelService()
