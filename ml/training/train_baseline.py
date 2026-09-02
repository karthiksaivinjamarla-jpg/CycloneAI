"""Minimal training loop for the CycloneAI multi-task baseline.

The script intentionally accepts tensors prepared by the data pipeline rather
than reading raw satellite archives. This keeps dataset handling separate from
model training and makes experiments reproducible.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def train_epoch(model: Any, loader: Any, optimizer: Any, device: Any) -> float:
    import torch
    from ml.models.losses import multitask_loss

    model.train()
    total = 0.0
    count = 0
    for batch in loader:
        x = batch["images"].to(device)
        targets = {k: v.to(device) for k, v in batch["targets"].items()}
        optimizer.zero_grad(set_to_none=True)
        outputs = model(x)
        loss = multitask_loss(outputs, targets)
        loss.backward()
        optimizer.step()
        total += float(loss.detach())
        count += 1
    return total / max(count, 1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--output", type=Path, default=Path("ml/artifacts/baseline.pt"))
    args = parser.parse_args()

    import torch
    from torch.optim import AdamW
    from ml.models.multitask import build_model

    torch.manual_seed(42)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = build_model().to(device)

    # Dataset/DataLoader construction belongs to the dataset adapter. Keeping
    # this explicit prevents accidental training on unverified raw archives.
    raise SystemExit(
        "Training adapter is not configured yet. Prepare a verified storm-level "
        "dataset/DataLoader, then connect it before running this script."
    )


if __name__ == "__main__":
    main()
