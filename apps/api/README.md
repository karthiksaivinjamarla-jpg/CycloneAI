# CycloneAI API

FastAPI service boundary for SIH26070. The current analyzer is intentionally a prototype adapter; replace `app/services/analyzer.py::analyze()` with the trained model inference pipeline when the ML model is ready.

## Run locally

```bash
cd apps/api
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Health check: `GET /health`

Analysis: `POST /api/v1/analyze`
