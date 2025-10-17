"""Deny direct pip usage."""

import re
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def pip_direct_deny_rule(input_data: ToolUseEvent):
    """Deny direct pip usage - use uv run pip or uv sync instead."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Match direct pip usage (but not uv run pip)
    if re.match(r'^pip(\d+(\.\d+)?)?\s+', command):
        yield PolicyHelper.deny(
            "Direct pip usage is not allowed.\n"
            "Use 'uv run pip' or 'uv sync' to manage dependencies."
        )
