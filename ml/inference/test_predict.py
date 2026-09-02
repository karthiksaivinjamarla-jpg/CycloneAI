import numpy as np
import torch

from ml.inference.predict import CyclonePredictor
from ml.models.cnn_gru import CNNGRUMultiTaskNet


def test_predictor_loads_checkpoint_and_returns_contract(tmp_path):
    model = CNNGRUMultiTaskNet()
    checkpoint = tmp_path / "model.pt"
    torch.save({
        "model_state_dict": model.state_dict(),
        "model_version": "test-v1",
        "channels": ["IR", "WV", "VIS", "MW"],
    }, checkpoint)

    predictor = CyclonePredictor(checkpoint, device="cpu")
    sequence = np.zeros((4, 4, 32, 32), dtype=np.float32)
    result = predictor.predict(sequence)

    assert result["model_version"] == "test-v1"
    assert "cyclone_detected" in result
    assert "classification" in result
    assert "intensity" in result
    assert "track_offset" in result
