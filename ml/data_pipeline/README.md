# Data pipeline

Dataset ingestion lives here. Keep downloads separate from preprocessing so source-specific formats do not leak into model code.

## First real-data workflow

The repository does **not** contain raw satellite archives. Keep those files in local/external storage and create a small JSONL satellite manifest.

One line per channel frame:

```json
{"storm_id":"2020-01","timestamp":"2020-05-16T06:00:00+00:00","source":"TCIR","channel":"IR","path":"/data/tcir/2020-01/ir.nc"}
```

Supported channels: `IR`, `WV`, `VIS`, `MW`.

From the repository root:

```bash
python -m ml.data_pipeline.manifest_from_joined path/to/ibtracs.csv path/to/satellite.jsonl data/manifests/all.jsonl
```

The command:

1. loads North Indian Ocean (`NI`) IBTrACS records;
2. joins the nearest satellite frame for each available channel;
3. creates a 24-hour future track target;
4. derives the IMD cyclone class from wind speed;
5. stores file references plus labels in JSONL.

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

A missing satellite channel is allowed by the join stage and is zero-filled by the tensorizer unless `require_channels=True`. For the first real experiment, record channel coverage and compare results for complete vs partial multi-source inputs.

The current baseline is a single-frame CNN. Temporal sequence modeling will be added after the data pipeline is validated on real North Indian Ocean storms.
