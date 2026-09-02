from ml.evaluation.track_metrics import haversine_km, mean_track_error_km


def test_haversine_zero_distance():
    assert haversine_km(10.0, 80.0, 10.0, 80.0) == 0.0


def test_origin_aware_offset_error():
    origins = [(10.0, 80.0), (15.0, 85.0)]
    actual = [(1.0, 1.0), (0.5, -0.5)]
    predicted = [(1.0, 1.0), (0.5, -0.5)]
    assert mean_track_error_km(origins, predicted, actual) == 0.0


def test_track_error_is_positive_when_destination_changes():
    origins = [(10.0, 80.0)]
    actual = [(1.0, 1.0)]
    predicted = [(2.0, 1.0)]
    assert mean_track_error_km(origins, predicted, actual) > 100.0
