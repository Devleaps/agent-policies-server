"""
Policy for commands that are always whitelisted with any parameters.

These commands pose no security risk and can be executed freely:
- pwd: Print working directory
- ps: Process status
- lsof: List open files
- which: Locate command binaries
- grep: Search patterns in text
- nslookup: DNS queries
- pkill: Kill processes by name
- pytest: Run tests
- tflint: Terraform linter
"""

import re
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


# List of commands that are always allowed
ALWAYS_ALLOWED_COMMANDS = [
    "pwd",
    "ps",
    "lsof",
    "which",
    "grep",
    "nslookup",
    "pkill",
    "pytest",
    "tflint",
]


def whitelist_always_rule(input_data: ToolUseEvent):
    """Allows whitelisted commands with any parameters."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Check if command starts with any of the whitelisted commands
    for cmd in ALWAYS_ALLOWED_COMMANDS:
        if re.match(rf'^{re.escape(cmd)}(?:\s|$)', command):
            yield PolicyHelper.allow()
            return

    return None


# Export single rule
all_rules = [whitelist_always_rule]
