"""
Which command policy rule.

This rule allows which commands to locate executables.
"""

import re
from typing import Optional
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def which_rule(input_data: ToolUseEvent):
    """Allows which commands to locate executables."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Allow which commands (with or without arguments)
    if re.match(r'^which(?:\s|$)', command):
        yield PolicyHelper.allow()

    return None