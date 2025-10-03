"""
Git status policy rule.

This rule allows git status commands.
"""

import re
from typing import Optional
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def git_status_rule(input_data: ToolUseEvent):
    """Allows git status commands."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Allow git status (with or without options)
    if re.match(r'^git\s+status(?:\s|$)', command):
        yield PolicyHelper.allow()

    return None