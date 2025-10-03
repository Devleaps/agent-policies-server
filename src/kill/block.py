"""
Kill policy rule that blocks kill commands.

This rule blocks kill commands and recommends using pkill instead for safer process termination.
"""

import re
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def kill_block_rule(input_data: ToolUseEvent):
    """Blocks kill commands and recommends pkill."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Block kill commands
    if re.match(r'^kill(?:\s|$)', command):
        yield PolicyHelper.deny(
            "By policy, kill commands are not allowed.\n"
            "Use `pkill` instead for safer process termination (e.g., `pkill -f processname`)."
        )