from app.schemas.analysis import AnalysisRequest, AnalysisResponse, TrackPoint


def analyze(request: AnalysisRequest) -> AnalysisResponse:
    """Prototype adapter. Replace this function with the trained ML inference call."""
    observed = [
        TrackPoint(hours=-18, latitude=request.latitude - 2.0, longitude=request.longitude - 2.2, wind_knots=74),
        TrackPoint(hours=-12, latitude=request.latitude - 1.6, longitude=request.longitude - 1.4, wind_knots=77),
        TrackPoint(hours=-6, latitude=request.latitude - 1.2, longitude=request.longitude - 0.6, wind_knots=80),
    ]

    forecast = [
        TrackPoint(hours=6, latitude=request.latitude + 0.6, longitude=request.longitude + 0.7, wind_knots=84, uncertainty_km=35),
        TrackPoint(hours=12, latitude=request.latitude + 1.2, longitude=request.longitude + 1.5, wind_knots=86, uncertainty_km=55),
        TrackPoint(hours=24, latitude=request.latitude + 2.0, longitude=request.longitude + 2.7, wind_knots=88, uncertainty_km=85),
        TrackPoint(hours=36, latitude=request.latitude + 2.8, longitude=request.longitude + 3.8, wind_knots=82, uncertainty_km=120),
        TrackPoint(hours=48, latitude=request.latitude + 3.6, longitude=request.longitude + 4.7, wind_knots=74, uncertainty_km=160),
    ]

    return AnalysisResponse(
        cyclone_detected=True,
        classification={"label": "Very Severe Cyclonic Storm", "confidence": 0.91},
        intensity={"wind_knots": 82, "pressure_hpa": 970},
        center={"latitude": request.latitude, "longitude": request.longitude},
        movement={"direction": "NW", "speed_knots": 12},
        observed_track=observed,
        track=forecast,
        explainability={"labels": ["Deep convection", "Curved banding", "Eye structure"], "heatmap_url": None},
        model={"version": "api-mock-v0.1", "generated_at": request.timestamp.isoformat()},
    )
