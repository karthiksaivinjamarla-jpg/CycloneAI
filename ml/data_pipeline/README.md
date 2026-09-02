# Data pipeline

Dataset ingestion lives here. Keep downloads separate from preprocessing so source-specific formats do not leak into model code.

## First implementation

Create a loader for IBTrACS track records and normalize each record into the repository's `Observation` contract in `ml/data_pipeline.py`.

Then add a satellite loader for TCIR/HURSAT-compatible frames and join observations by storm ID and timestamp.

### Required metadata

- storm ID / name
- basin
- observation timestamp
- latitude / longitude
- wind speed and pressure when available
- source dataset and version
- satellite channels present
- source file identifier/checksum

Raw data should remain outside GitHub.
