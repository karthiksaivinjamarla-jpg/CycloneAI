from datetime import datetime
from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    timestamp: datetime
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    sources: list[str] = Field(default_factory=list)


class TrackPoint(BaseModel):
    hours: int
    latitude: float
    longitude: float
    wind_knots: float
    uncertainty_km: float | None = None


class AnalysisResponse(BaseModel):
    cyclone_detected: bool
    classification: dict[str, float | str]
    intensity: dict[str, float]
    center: dict[str, float]
    movement: dict[str, float | str]
    observed_track: list[TrackPoint] = Field(default_factory=list)
    track: list[TrackPoint]
    explainability: dict[str, object]
    model: dict[str, str]
