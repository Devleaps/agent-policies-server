"""
Gemini AfterTool hook models.
"""

from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict

from .common import GeminiBaseOutput


class AfterToolInput(BaseModel):
    """Input for Gemini AfterTool hook."""

    model_config = ConfigDict(extra="allow")

    session_id: str
    hook_event_name: str
    tool_name: str
    tool_input: Optional[Dict[str, Any]] = None
    cwd: Optional[str] = None
    timestamp: Optional[str] = None
    tool_response: Optional[Dict[str, Any]] = None


class AfterToolHookSpecificOutput(BaseModel):
    """Hook-specific output for AfterTool hook."""

    additionalContext: Optional[str] = None


class AfterToolOutput(GeminiBaseOutput):
    """Output for Gemini AfterTool hook."""

    hookSpecificOutput: Optional[AfterToolHookSpecificOutput] = None
