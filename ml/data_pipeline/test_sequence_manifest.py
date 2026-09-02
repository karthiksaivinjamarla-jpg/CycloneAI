from datetime import datetime, timedelta

from ml.data_pipeline.build_sequence_manifest import build_labeled_sequences


def test_build_labeled_sequences_attaches_current_and_future_labels():
    start = datetime(2025, 1, 1, 0, 0)
    frames = []
    for step in range(5):
        timestamp = start + timedelta(hours=step * 3)
        frames.append({
            "storm_id": "TEST01",
            "timestamp": timestamp.isoformat(),
            "image_paths": {"IR": f"ir-{step}.nc"},
            "available_channels": ["IR"],
        })

    tracks = [
        type("Track", (), {
            "storm_id": "TEST01",
            "timestamp": start + timedelta(hours=step * 3),
            "latitude": 10.0 + step,
            "longitude": 80.0 + step,
            "wind_knots": 50.0,
            "pressure_hpa": 990.0,
        })()
        for step in range(5)
    ]

    records = build_labeled_sequences(
        frames,
        tracks,
        sequence_length=4,
        cadence_hours=3,
        tolerance_minutes=90,
        forecast_hours=3,
    )

    assert len(records) == 2
    record = records[0]
    assert len(record["frames"]) == 4
    assert record["detected"] is True
    assert record["class_index"] == 3
    assert record["wind_knots"] == 50.0
    assert record["track_offsets"] == [[1.0, 1.0]]
    assert record["forecast_hours"] == 3
