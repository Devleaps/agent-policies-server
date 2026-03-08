"""
Gemini BeforeTool hook models.
"""

from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict

from .common import GeminiBaseOutput


class BeforeToolInput(BaseModel):
    """Input for Gemini BeforeTool hook."""

    model_config = ConfigDict(extra="allow")

    session_id: str
    hook_event_name: str
    tool_name: str
    tool_input: Optional[Dict[str, Any]] = None
    cwd: Optional[str] = None
    timestamp: Optional[str] = None


class BeforeToolHookSpecificOutput(BaseModel):
    """Hook-specific output for BeforeTool hook."""

    tool_input: Optional[Dict[str, Any]] = None


class BeforeToolOutput(GeminiBaseOutput):
    """Output for Gemini BeforeTool hook."""

    hookSpecificOutput: Optional[BeforeToolHookSpecificOutput] = None
