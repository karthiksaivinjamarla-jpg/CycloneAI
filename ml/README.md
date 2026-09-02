# CycloneAI ML

ML workspace for SIH26070: cyclone identification, classification, intensity estimation, track prediction and explainability.

## Planned flow

1. Ingest historical cyclone tracks (IBTrACS or an approved equivalent).
2. Ingest satellite observations (IR/WV/VIS/PMW where available).
3. Align satellite frames with best-track timestamps and storm centers.
4. Create storm-level train/validation/test splits to avoid temporal/frame leakage.
5. Train a baseline satellite classifier/intensity estimator.
6. Add a temporal model for future track prediction.
7. Evaluate on a dedicated North Indian Ocean subset.
8. Export an inference artifact for the FastAPI adapter.

The repository currently contains scaffolding only; no trained model or benchmark is claimed here.
