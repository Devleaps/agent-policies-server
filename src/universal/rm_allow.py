"""Blocks all rm commands and suggests trash instead."""

import re
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def rm_safe_operations_rule(input_data: ToolUseEvent):
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Match rm commands
    if not re.match(r'^rm\s+', command):
        return

    # Block all rm commands
    yield PolicyHelper.deny(
        "The `rm` command is not allowed.\n"
        "Always use `trash` instead. The macOS `trash` command safely moves files to Trash."
    )
