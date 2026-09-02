"""FastAPI application for solar-and-storage optimization."""

from fastapi import FastAPI

from solar_and_storage.api.routers import router

app = FastAPI(
    title="Solar and Storage Optimization API",
    description="API for optimizing battery storage with solar generation",
    version="1.0.0",
)

app.include_router(router, prefix="/api/v1", tags=["optimization"])


@app.get("/health")
def health() -> dict[str, str]:
    """Health check endpoint.

    Returns:
        Health status dictionary.
    """
    return {"status": "healthy"}
