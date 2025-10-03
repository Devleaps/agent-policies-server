"""
PS (process status) policy rule for safe operations.

This rule allows ps commands to view running processes.
"""

import re
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def ps_allow_rule(input_data: ToolUseEvent):
    """Allows ps commands to view processes."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Allow ps command with various options
    if re.match(r'^ps(?:\s|$)', command):
        yield PolicyHelper.allow()