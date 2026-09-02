"""PyTorch dataset for fused temporal satellite sequences."""

from __future__ import annotations

import json
from pathlib import Path

import torch
from torch.utils.data import Dataset

from ml.data_pipeline.tensorize import load_multichannel_tensor


class CycloneSequenceDataset(Dataset):
    """Load sequence manifests into [T,C,H,W] tensors and multitask targets."""

    def __init__(self, manifest_path: str | Path, frame_size: int = 201) -> None:
        self.records = [
            json.loads(line)
            for line in Path(manifest_path).read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        self.frame_size = frame_size

    def __len__(self) -> int:
        return len(self.records)

    def __getitem__(self, index: int) -> dict[str, torch.Tensor]:
        record = self.records[index]
        frames = record["frames"]
        tensors = [
            load_multichannel_tensor(frame["image_paths"], size=self.frame_size)
            for frame in frames
        ]
        sequence = torch.from_numpy(__import__("numpy").stack(tensors)).float()
        return {
            "images": sequence,
            "targets": {
                "detected": torch.tensor(float(record.get("detected", True))),
                "class_index": torch.tensor(int(record.get("class_index", 0))),
                "wind_knots": torch.tensor(float(record.get("wind_knots", 0.0))),
                "track_offsets": torch.tensor(record.get("track_offsets", [[0.0, 0.0]]), dtype=torch.float32),
            },
        }
