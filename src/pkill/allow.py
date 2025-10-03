"""
Pkill policy rule for safe process termination.

This rule allows pkill commands to terminate processes by name/pattern.
"""

import re
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def pkill_allow_rule(input_data: ToolUseEvent):
    """Allows pkill commands to terminate processes."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Allow pkill command with various options
    if re.match(r'^pkill(?:\s|$)', command):
        yield PolicyHelper.allow()