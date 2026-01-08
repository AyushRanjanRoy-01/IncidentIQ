"""FastAPI application entry point.

This module initializes the FastAPI application with middleware,
event handlers, and route registration.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AI-SRE Platform API",
    description="Automated incident detection, RCA, and self-healing platform",
    version="0.1.0"
)

# TODO: Add CORS middleware configuration
# TODO: Register API routes (v1)
# TODO: Add startup/shutdown event handlers
# TODO: Add health check endpoint

@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    # Minimal health response for local development and probes
    return {"status": "ok", "version": "0.1.0"}
