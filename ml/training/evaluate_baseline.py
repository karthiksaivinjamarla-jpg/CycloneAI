"""Evaluate a trained CycloneAI baseline on a prepared JSONL manifest."""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("checkpoint", type=Path)
    parser.add_argument("--batch-size", type=int, default=16)
    args = parser.parse_args()

    import torch
    from torch.utils.data import DataLoader
    from ml.data_pipeline.dataset import CycloneDataset
    from ml.models.multitask import build_model
    from ml.evaluation.metrics import mean_absolute_error, track_error_km

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    dataset = CycloneDataset(args.manifest)
    loader = DataLoader(dataset, batch_size=args.batch_size, shuffle=False)
    checkpoint = torch.load(args.checkpoint, map_location=device, weights_only=False)
    model = build_model().to(device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    class_correct = class_total = 0
    wind_errors: list[float] = []
    track_errors: list[float] = []

    with torch.no_grad():
        for batch in loader:
            outputs = model(batch["images"].to(device))
            targets = batch["targets"]
            predicted_class = outputs["class_logits"].argmax(dim=1).cpu().tolist()
            actual_class = targets["class_index"].tolist()
            class_correct += sum(p == a for p, a in zip(predicted_class, actual_class))
            class_total += len(actual_class)
            wind_errors.extend(mean_absolute_error(outputs["intensity"].squeeze(1).cpu().tolist(), targets["wind_knots"].tolist()) for _ in [0])

            predicted_track = outputs["track"].cpu().tolist()
            actual_track = targets["track_offsets"].cpu().tolist()
            for pred, actual in zip(predicted_track, actual_track):
                # Current baseline contains one forecast point per sample.
                track_errors.append(track_error_km(0.0, 0.0, pred[0][0], pred[0][1], actual[0], actual[1]))

    accuracy = class_correct / max(class_total, 1)
    print(f"classification_accuracy={accuracy:.4f}")
    print(f"intensity_mae_knots={sum(wind_errors) / max(len(wind_errors), 1):.4f}")
    print(f"track_error_km={sum(track_errors) / max(len(track_errors), 1):.4f}")


if __name__ == "__main__":
    main()
