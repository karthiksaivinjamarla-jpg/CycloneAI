# Data pipeline

The first reproducible experiment uses **IBTrACS** for storm-track labels and **TCIR** for satellite frames. Raw archives are intentionally kept outside Git.

## 1. Prepare IBTrACS

Download an approved IBTrACS CSV and keep it under a local data directory. The loader filters the North Indian Ocean basin using the IBTrACS `NI` basin code and extracts timestamp, position, wind and pressure fields.

## 2. Prepare TCIR metadata

TCIR's exact archive layout can vary by release/download method, so do not hard-code an assumed directory structure. Create a metadata CSV containing:

```text
storm_id,timestamp,channel,path,latitude,longitude
```

`latitude` and `longitude` are optional. `channel` must be one of `IR,WV,VIS,MW`.

Convert it to normalized satellite JSONL:

```bash
python -m ml.data_pipeline.build_tcir_manifest \
  data/raw/tcir_metadata.csv \
  data/raw/tcir_satellite.jsonl
```

The resulting paths must point to files available on the machine running the training pipeline.

## 3. Build the training manifest

The joined-data builder matches track observations to the nearest satellite frame within the configured tolerance, then creates a 24-hour forecast sample. The current baseline uses one input frame and one 24-hour target point.

```bash
python -m ml.data_pipeline.manifest_from_joined \
  data/raw/ibtracs.csv \
  data/raw/tcir_satellite.jsonl \
  data/manifests/all.jsonl
```

## 4. Split by storm

Never randomly split individual frames. Storm-level splitting prevents frames from the same cyclone appearing in both training and test sets.

```bash
python -m ml.training.split_manifest \
  data/manifests/all.jsonl \
  --output-dir data/manifests/splits
```

## 5. Train the baseline

```bash
python -m ml.training.train_baseline \
  data/manifests/splits/train.jsonl \
  --epochs 20 \
  --batch-size 16 \
  --output ml/artifacts/baseline.pt
```

## 6. Evaluate

```bash
python -m ml.training.evaluate_baseline \
  data/manifests/splits/test.jsonl \
  ml/artifacts/baseline.pt
```

### Important baseline limitations

- The current manifest contains cyclone-positive samples only, so the detection head is **not yet a meaningful cyclone-vs-no-cyclone benchmark**. Non-cyclone satellite samples must be added before reporting detection precision/recall/F1.
- The current track target is a single 24-hour point. Multi-step +6/+12/+24/+48-hour forecasting comes after this baseline is reproducible.
- Channel normalization is currently generic; production training should use channel-specific statistics calculated from the training split.
- Raw TCIR/IBTrACS archives are not committed to GitHub.
