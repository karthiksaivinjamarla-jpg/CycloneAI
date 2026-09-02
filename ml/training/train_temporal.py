"""Train the CNN-GRU temporal multi-task model."""

from __future__ import annotations

import argparse
import random

import numpy as np
import torch
from torch.utils.data import DataLoader

from ml.data_pipeline.sequence_dataset import CycloneSequenceDataset
from ml.models.cnn_gru import CNNGRUMultiTaskNet
from ml.models.losses import multitask_loss


def train_epoch(model, loader, optimizer, device):
    model.train()
    total = 0.0
    for batch in loader:
        images = batch["images"].to(device)
        targets = {key: value.to(device) for key, value in batch["targets"].items()}
        optimizer.zero_grad(set_to_none=True)
        loss = multitask_loss(model(images), targets)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        total += loss.item()
    return total / max(len(loader), 1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest")
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--workers", type=int, default=0)
    parser.add_argument("--sequence-length", type=int, default=4)
    parser.add_argument("--output", default="ml/checkpoints/cnn-gru-v0.1.pt")
    args = parser.parse_args()

    random.seed(42)
    np.random.seed(42)
    torch.manual_seed(42)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    dataset = CycloneSequenceDataset(args.manifest)
    if len(dataset) == 0:
        raise ValueError("manifest contains no sequence samples")
    if args.sequence_length != 4:
        raise ValueError("current model expects the 4-frame sequence contract")

    loader = DataLoader(dataset, batch_size=args.batch_size, shuffle=True, num_workers=args.workers)
    model = CNNGRUMultiTaskNet().to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)

    best_loss = float("inf")
    for epoch in range(1, args.epochs + 1):
        loss = train_epoch(model, loader, optimizer, device)
        print(f"epoch={epoch} train_loss={loss:.6f}")
        if loss < best_loss:
            best_loss = loss
            output = args.output
            import os
            os.makedirs(os.path.dirname(output) or ".", exist_ok=True)
            torch.save({
                "model_state_dict": model.state_dict(),
                "model_version": "cnn-gru-v0.1",
                "sequence_length": 4,
                "channels": ["IR", "WV", "VIS", "MW"],
                "best_train_loss": best_loss,
            }, output)


if __name__ == "__main__":
    main()
