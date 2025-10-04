"""
Policy for commands that are always whitelisted with any parameters.
"""

import re
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


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

ALLOWED_SUBCOMMANDS = [
    ["git", "status"],
    ["git", "diff"],
    ["git", "log"],
    ["git", "show"],
    ["terraform", "fmt"],
    ["terraform", "plan"],
    ["terragrunt", "plan"],
    ["source", "venv/bin/activate"],
]


def whitelist_always_rule(input_data: ToolUseEvent):
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Check if command starts with any of the whitelisted commands
    for cmd in ALWAYS_ALLOWED_COMMANDS:
        if re.match(rf'^{re.escape(cmd)}(?:\s|$)', command):
            yield PolicyHelper.allow()
            return

    # Check if command matches any allowed subcommands
    for subcommand_parts in ALLOWED_SUBCOMMANDS:
        # Build regex pattern from subcommand parts
        # Escape each part and join with \s+
        escaped_parts = [re.escape(part) for part in subcommand_parts]
        pattern = r'^' + r'\s+'.join(escaped_parts) + r'(?:\s|$)'

        if re.match(pattern, command):
            yield PolicyHelper.allow()
            return

    return None


# Export single rule
all_rules = [whitelist_always_rule]
