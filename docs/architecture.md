# Architecture

```text
React + TypeScript dashboard
        |
        v
Typed analysis service
        |
        +--> mock adapter (current prototype)
        |
        +--> FastAPI /api/v1/analyze (planned)
                    |
                    v
             ML inference service
```

The frontend does not contain training code. It consumes a stable analysis contract so the ML implementation can evolve independently.
