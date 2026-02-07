"""
Consolidated hook input/output models for simple Claude Code hooks.

These hooks have minimal I/O requirements. Complex hooks (PreToolUse, PostToolUse)
remain in their own modules.
"""

from typing import Literal, Optional

from pydantic import BaseModel

from .output_base import BaseHookOutput, BaseBlockingHookOutput

# ============================================================================
# Notification
# ============================================================================


class NotificationInput(BaseModel):
    """Input for Notification hook based on Claude Code documentation."""

    session_id: str
    transcript_path: str
    cwd: str
    hook_event_name: Literal["Notification"]
    message: str


class NotificationOutput(BaseHookOutput):
    """Output for Notification hook based on Claude Code documentation."""

    pass


# ============================================================================
# PreCompact
# ============================================================================


class PreCompactInput(BaseModel):
    """Input for PreCompact hook based on Claude Code documentation."""

    session_id: str
    transcript_path: str
    hook_event_name: Literal["PreCompact"]
    trigger: str
    custom_instructions: str


class PreCompactOutput(BaseHookOutput):
    """Output for PreCompact hook based on Claude Code documentation."""

    pass


# ============================================================================
# SessionEnd
# ============================================================================


class SessionEndInput(BaseModel):
    """Input for SessionEnd hook based on Claude Code documentation."""

    session_id: str
    transcript_path: str
    cwd: str
    hook_event_name: Literal["SessionEnd"]
    reason: str


class SessionEndOutput(BaseHookOutput):
    """Output for SessionEnd hook based on Claude Code documentation."""

    pass


# ============================================================================
# SessionStart
# ============================================================================


class SessionStartInput(BaseModel):
    """Input for SessionStart hook based on Claude Code documentation."""

    session_id: str
    transcript_path: str
    hook_event_name: Literal["SessionStart"]
    source: str


class SessionStartHookSpecificOutput(BaseModel):
    """Hook-specific output for SessionStart hook."""

    hookEventName: str = "SessionStart"
    additionalContext: Optional[str] = None


class SessionStartOutput(BaseHookOutput):
    """Output for SessionStart hook based on Claude Code documentation."""

    hookSpecificOutput: Optional[SessionStartHookSpecificOutput] = None


# ============================================================================
# Stop / SubagentStop
# ============================================================================


class StopInput(BaseModel):
    """Input for Stop hook based on Claude Code documentation."""

    session_id: str
    transcript_path: str
    hook_event_name: Literal["Stop"]
    stop_hook_active: Optional[bool] = None


class SubagentStopInput(BaseModel):
    """Input for SubagentStop hook based on Claude Code documentation."""

    session_id: str
    transcript_path: str
    hook_event_name: Literal["SubagentStop"]
    stop_hook_active: Optional[bool] = None


class StopOutput(BaseBlockingHookOutput):
    """Output for Stop hook based on Claude Code documentation."""

    pass


class SubagentStopOutput(BaseBlockingHookOutput):
    """Output for SubagentStop hook based on Claude Code documentation."""

    pass


# ============================================================================
# UserPromptSubmit
# ============================================================================


class UserPromptSubmitInput(BaseModel):
    """Input for UserPromptSubmit hook based on Claude Code documentation."""

    session_id: str
    transcript_path: str
    cwd: str
    hook_event_name: Literal["UserPromptSubmit"]
    prompt: str


class UserPromptSubmitHookSpecificOutput(BaseModel):
    """Hook-specific output for UserPromptSubmit hook."""

    hookEventName: str = "UserPromptSubmit"
    additionalContext: Optional[str] = None


class UserPromptSubmitOutput(BaseBlockingHookOutput):
    """Output for UserPromptSubmit hook based on Claude Code documentation."""

    hookSpecificOutput: Optional[UserPromptSubmitHookSpecificOutput] = None
