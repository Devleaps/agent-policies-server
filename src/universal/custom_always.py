"""
Policy for custom commands that are always whitelisted with any parameters.
"""

import re
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


CUSTOM_ALLOWED_COMMANDS = [
    "presentations",
]


def custom_always_rule(input_data: ToolUseEvent):
    """Allow custom whitelisted commands with any parameters."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Check if command starts with any of the custom allowed commands
    for cmd in CUSTOM_ALLOWED_COMMANDS:
        if re.match(rf'^{re.escape(cmd)}(?:\s|$)', command):
            yield PolicyHelper.allow()
            return

    return None


# Export single rule
all_rules = [custom_always_rule]
