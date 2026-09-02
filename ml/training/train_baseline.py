"""Train the CycloneAI multi-task CNN baseline from a prepared JSONL manifest."""

from __future__ import annotations

import argparse
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
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--workers", type=int, default=0)
    parser.add_argument("--output", type=Path, default=Path("ml/artifacts/baseline.pt"))
    args = parser.parse_args()

    import torch
    from torch.optim import AdamW
    from torch.utils.data import DataLoader
    from ml.data_pipeline.dataset import CycloneDataset
    from ml.models.multitask import build_model

    if not args.manifest.exists():
        raise SystemExit(f"Manifest not found: {args.manifest}")

    torch.manual_seed(42)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    dataset = CycloneDataset(args.manifest)
    if len(dataset) == 0:
        raise SystemExit("Manifest contains no training records")

    loader = DataLoader(dataset, batch_size=args.batch_size, shuffle=True, num_workers=args.workers)
    model = build_model().to(device)
    optimizer = AdamW(model.parameters(), lr=args.lr)

    print(f"device={device} samples={len(dataset)} batches={len(loader)}")
    for epoch in range(1, args.epochs + 1):
        loss = train_epoch(model, loader, optimizer, device)
        print(f"epoch={epoch:03d} loss={loss:.6f}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"model_state_dict": model.state_dict(), "model_version": "baseline-cnn-v0.1"}, args.output)
    print(f"saved={args.output}")


if __name__ == "__main__":
    main()
