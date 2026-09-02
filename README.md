# CycloneAI

AI-assisted multi-source tropical cyclone intelligence dashboard for SIH26070.

## Current build

The first website layer is implemented as a React + TypeScript + Vite dashboard. It intentionally uses mock analysis values so the UI can be developed before the ML model is handed over.

### Dashboard modules
- Bay of Bengal storm map with observed vs AI forecast track
- Current cyclone classification, wind, pressure, position and confidence
- IR / Water Vapor / Visible / Microwave source controls
- Track + intensity forecast table for 6–48 hour horizons
- Explainability panel prepared for Grad-CAM/attention output
- Historical replay / model metrics / data-source navigation placeholders
- Responsive mobile layout
- Model integration CTA and loading state

## Planned integration contract

The frontend should consume a stable API response rather than model internals:

```json
{
  "cyclone_detected": true,
  "classification": { "label": "Very Severe Cyclonic Storm", "confidence": 0.91 },
  "intensity": { "wind_knots": 82, "pressure_hpa": 970 },
  "track": [
    { "hours": 6, "latitude": 15.8, "longitude": 83.1 },
    { "hours": 12, "latitude": 16.4, "longitude": 83.9 },
    { "hours": 24, "latitude": 17.2, "longitude": 85.1 }
  ]
}
```

This keeps the web app independent from the ML implementation and lets the model team replace training/inference code without rewriting the dashboard.

## Local development

```bash
npm install
npm run dev
```

## Next milestones

1. Add typed API service layer and mock adapter.
2. Add real map rendering with MapLibre/Leaflet.
3. Add FastAPI backend endpoint.
4. Connect the friend's inference model.
5. Replace mock metrics with model outputs.
6. Add historical cyclone replay and actual-vs-predicted evaluation.
7. Add model/data version metadata and production deployment.
