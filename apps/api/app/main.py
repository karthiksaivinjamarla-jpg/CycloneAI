from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.schemas.analysis import AnalysisRequest, AnalysisResponse
from app.services.analyzer import analyze
from app.services.model_service import model_service

app = FastAPI(
    title="CycloneAI API",
    version="0.2.0",
    description="AI-assisted tropical cyclone analysis API for SIH26070.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "service": "cyclone-ai-api",
        "model_available": model_service.available,
    }


@app.post("/api/v1/analyze", response_model=AnalysisResponse)
def run_analysis(request: AnalysisRequest) -> AnalysisResponse:
    # Keep the deterministic analyzer as a development fallback until a real
    # trained checkpoint is installed. The trained-model path is now isolated
    # behind ModelService so it can replace this adapter without changing the API.
    return analyze(request)
