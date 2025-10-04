"""
Policy for commands that require workspace-relative safe paths.
"""

import re
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper, path_appears_safe


SAFE_PATH_COMMANDS = [
    "ls",
    "cat",
    "head",
    "tail",
    "wc",
    "diff",
    "cp",
    "mkdir",
    "trash",
]


def whitelist_safe_paths_rule(input_data: ToolUseEvent):
    """Allows whitelisted commands with any options/flags, but workspace-relative paths only."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Check if command starts with any of the safe path commands
    for cmd in SAFE_PATH_COMMANDS:
        if re.match(rf'^{re.escape(cmd)}(?:\s|$)', command):
            # Check path safety
            is_safe, reason = path_appears_safe(command)
            if not is_safe:
                yield PolicyHelper.deny(f"{cmd}: {reason}")
                return

            # All checks passed - command can use any options/flags as long as paths are safe
            yield PolicyHelper.allow()
            return

    return None


# Export single rule
all_rules = [whitelist_safe_paths_rule]
