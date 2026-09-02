from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.schemas.analysis import AnalysisRequest, AnalysisResponse
from app.services.analyzer import analyze

app = FastAPI(
    title="CycloneAI API",
    version="0.1.0",
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
def health() -> dict[str, str]:
    return {"status": "ok", "service": "cyclone-ai-api"}


@app.post("/api/v1/analyze", response_model=AnalysisResponse)
def run_analysis(request: AnalysisRequest) -> AnalysisResponse:
    return analyze(request)
