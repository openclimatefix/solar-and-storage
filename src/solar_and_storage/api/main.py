"""FastAPI application for solar-and-storage optimization."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from solar_and_storage.api.routers import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler.

    Args:
        _app: FastAPI application instance.

    Yields:
        None
    """
    logger.info("Starting solar-and-storage API server")
    yield
    logger.info("Shutting down solar-and-storage API server")


# Initialize FastAPI application
app = FastAPI(
    title="Solar and Storage Optimization API",
    description="API for optimizing battery storage with solar generation",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/api/v1", tags=["optimization"])


@app.get("/health")
def health() -> dict[str, str]:
    """Health check endpoint.

    Returns:
        Health status dictionary.
    """
    return {"status": "healthy"}
