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
    (r'^terraform\s+fmt(?:\s+[\w\-\.\/]+)?(?:\s|$)', "terraform fmt"),
    (r'^terraform\s+plan(?:\s|$)', "terraform plan"),
    (r'^terragrunt\s+plan(?:\s|$)', "terragrunt plan"),
    (r'^source\s+venv/bin/activate$', "source venv/bin/activate"),
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

    # Check if command matches any allowed subcommands
    for pattern, _ in ALLOWED_SUBCOMMANDS:
        if re.match(pattern, command):
            yield PolicyHelper.allow()
            return

    return None


# Export single rule
all_rules = [whitelist_always_rule]
