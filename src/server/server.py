import logging
import os

from fastapi import FastAPI

from .bundles import KNOWN_BUNDLES
from .bundles import router as bundles_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BUILD_VERSION = os.environ.get("VERSION", "unknown")
BUILD_GIT_SHA = os.environ.get("GIT_SHA", "unknown")

app = FastAPI(title="DevLeaps Policy Bundle Server", version=BUILD_VERSION)
app.include_router(bundles_router)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "AI Agent Policy Bundle Server by DevLeaps",
        "version": BUILD_VERSION,
        "git_sha": BUILD_GIT_SHA,
        "endpoints": {
            "bundles": [
                f"/bundles/composed?names=<comma-separated subset of {sorted(KNOWN_BUNDLES)}>"
            ],
        },
    }
