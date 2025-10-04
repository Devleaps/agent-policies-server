"""
Policy for commands that require workspace-relative safe paths.

These commands are only allowed with workspace-relative paths (no absolute paths,
no upward directory traversal with ..):
- ls: List directory contents
- cat: Display file contents
- head: Display beginning of files
- tail: Display end of files
- wc: Word/line/byte count
- diff: Compare files
- cp: Copy files
"""

import re
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper
from src.utils.heuristics import path_appears_safe


# List of commands that require safe paths
SAFE_PATH_COMMANDS = [
    "ls",
    "cat",
    "head",
    "tail",
    "wc",
    "diff",
    "cp",
]


def whitelist_safe_paths_rule(input_data: ToolUseEvent):
    """Allows whitelisted commands with workspace-relative paths only."""
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

            # All checks passed
            yield PolicyHelper.allow()
            return

    return None


# Export single rule
all_rules = [whitelist_safe_paths_rule]
