import logging
import os

from fastapi import FastAPI

from .bundles import KNOWN_BUNDLES
from .bundles import router as bundles_router
from .claude_code import router as claude_code_router
from .registry import registry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BUILD_VERSION = os.environ.get("VERSION", "unknown")
BUILD_GIT_SHA = os.environ.get("GIT_SHA", "unknown")

app = FastAPI(title="DevLeaps Policy Server", version=BUILD_VERSION)
app.include_router(claude_code_router)
app.include_router(bundles_router)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "AI Agent Policy Server by DevLeaps",
        "version": BUILD_VERSION,
        "git_sha": BUILD_GIT_SHA,
        "editors": ["claude-code"],
        "endpoints": {
            "claude-code": [
                "/policy/claude-code/PreToolUse",
                "/policy/claude-code/PostToolUse",
                "/policy/claude-code/UserPromptSubmit",
                "/policy/claude-code/Stop",
                "/policy/claude-code/SubagentStop",
                "/policy/claude-code/Notification",
                "/policy/claude-code/PreCompact",
                "/policy/claude-code/SessionStart",
                "/policy/claude-code/SessionEnd",
            ],
            "bundles": [
                f"/bundles/composed?names=<comma-separated subset of {sorted(KNOWN_BUNDLES)}>"
            ],
        },
    }


def get_registry():
    """Get the global hook registry for registering handlers."""
    return registry
