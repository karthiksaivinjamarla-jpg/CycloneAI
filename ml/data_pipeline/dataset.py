"""PyTorch dataset adapter for prepared CycloneAI samples.

Expected manifest format is a JSONL file where each line contains:
{
  "image_paths": {"IR": "...", "WV": "...", "VIS": "...", "MW": "..."},
  "detected": true,
  "class_index": 3,
  "wind_knots": 55.0,
  "track_offsets": [[0.2, 0.4], [0.4, 0.8], [0.7, 1.1], [1.0, 1.5]]
}

Raw archives remain outside Git. This adapter consumes a curated manifest.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class CycloneDataset:
    def __init__(self, manifest_path: str | Path, frame_size: int = 201) -> None:
        try:
            import torch
            from torch.utils.data import Dataset
        except ImportError as exc:
            raise RuntimeError("Install PyTorch to use CycloneDataset") from exc

        class _Dataset(Dataset):
            def __init__(self, path: str | Path) -> None:
                self.records = [
                    json.loads(line)
                    for line in Path(path).read_text(encoding="utf-8").splitlines()
                    if line.strip()
                ]

            def __len__(self) -> int:
                return len(self.records)

            def __getitem__(self, index: int) -> dict[str, Any]:
                from ml.data_pipeline.tensorize import load_multichannel_tensor

                record = self.records[index]
                paths = record.get("image_paths", {})
                tensor = load_multichannel_tensor(paths, size=frame_size, require_channels=False)
                return {
                    "images": torch.from_numpy(tensor),
                    "targets": {
                        "detected": torch.tensor(record["detected"], dtype=torch.float32),
                        "class_index": torch.tensor(record["class_index"], dtype=torch.long),
                        "wind_knots": torch.tensor(record["wind_knots"], dtype=torch.float32),
                        "track_offsets": torch.tensor(record["track_offsets"], dtype=torch.float32),
                    },
                }

        self._dataset = _Dataset(manifest_path)

    def __len__(self) -> int:
        return len(self._dataset)

    def __getitem__(self, index: int) -> dict[str, Any]:
        return self._dataset[index]
