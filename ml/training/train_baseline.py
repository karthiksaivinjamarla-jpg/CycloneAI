"""Train the CycloneAI multi-task CNN baseline from prepared JSONL manifests."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any


def train_epoch(model: Any, loader: Any, optimizer: Any, device: Any) -> float:
    from ml.models.losses import multitask_loss

    model.train()
    total = 0.0
    count = 0
    for batch in loader:
        x = batch["images"].to(device)
        targets = {k: v.to(device) for k, v in batch["targets"].items()}
        optimizer.zero_grad(set_to_none=True)
        loss = multitask_loss(model(x), targets)
        loss.backward()
        optimizer.step()
        total += float(loss.detach())
        count += 1
    return total / max(count, 1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Train the CycloneAI CNN baseline")
    parser.add_argument("train_manifest", type=Path)
    parser.add_argument("--val-manifest", type=Path, default=None)
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
    from ml.evaluation.validate import evaluate
    from ml.models.multitask import build_model

    if not args.train_manifest.exists():
        raise SystemExit(f"Training manifest not found: {args.train_manifest}")
    if args.val_manifest and not args.val_manifest.exists():
        raise SystemExit(f"Validation manifest not found: {args.val_manifest}")

    torch.manual_seed(42)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    train_dataset = CycloneDataset(args.train_manifest)
    if len(train_dataset) == 0:
        raise SystemExit("Training manifest contains no records")
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True, num_workers=args.workers)

    val_loader = None
    if args.val_manifest:
        val_dataset = CycloneDataset(args.val_manifest)
        val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False, num_workers=args.workers)

    model = build_model().to(device)
    optimizer = AdamW(model.parameters(), lr=args.lr)
    best_val = float("inf")

    print(f"device={device} train_samples={len(train_dataset)}")
    for epoch in range(1, args.epochs + 1):
        train_loss = train_epoch(model, train_loader, optimizer, device)
        metrics = evaluate(model, val_loader, device) if val_loader and len(val_loader.dataset) else {}
        val_score = metrics.get("intensity_mae_knots", train_loss)
        print(f"epoch={epoch:03d} train_loss={train_loss:.6f} metrics={metrics}")
        if val_loader is None or val_score < best_val:
            best_val = val_score
            args.output.parent.mkdir(parents=True, exist_ok=True)
            torch.save({
                "model_state_dict": model.state_dict(),
                "model_version": "baseline-cnn-v0.2",
                "epoch": epoch,
                "validation_metrics": metrics,
            }, args.output)

    print(f"saved={args.output}")


if __name__ == "__main__":
    main()
