"""
Grep allow policy rule.

This rule allows all grep commands.
"""

import re
from typing import Optional
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def grep_allow_rule(input_data: ToolUseEvent):
    """Allows all grep commands."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Allow grep commands (with any options and patterns)
    if re.match(r'^grep(?:\s|$)', command):
        yield PolicyHelper.allow()

    return None