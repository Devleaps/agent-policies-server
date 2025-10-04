"""Blocks kill commands, recommends pkill instead."""

import re
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def kill_block_rule(input_data: ToolUseEvent):
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Block kill commands
    if re.match(r'^kill(?:\s|$)', command):
        yield PolicyHelper.deny(
            "By policy, kill commands are not allowed.\n"
            "Use `pkill` instead for safer process termination (e.g., `pkill -f processname`)."
        )