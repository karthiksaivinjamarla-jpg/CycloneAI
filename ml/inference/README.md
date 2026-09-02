# Inference

This package will contain the lightweight inference path used by the FastAPI service.

The production flow should load a versioned model artifact once at application startup, validate inputs, run preprocessing, execute the model, and return the API schema without exposing training-only dependencies to the web client.
