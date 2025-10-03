"""
LSOF (list open files) policy rule for safe operations.

This rule allows lsof commands to view open files and network connections.
"""

import re
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def lsof_allow_rule(input_data: ToolUseEvent):
    """Allows lsof commands to view open files and connections."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Allow lsof command with any options
    if re.match(r'^lsof(?:\s|$)', command):
        yield PolicyHelper.allow()