"""Allows mv with safe paths only (blocks absolute paths and upward traversal)."""

import re
from typing import Optional
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper, path_in_command_appears_safe


def mv_safe_operations_rule(input_data: ToolUseEvent):
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Match mv commands
    if not re.match(r'^mv\s+', command):
        return

    # Block mv with options/flags
    if re.search(r'^mv\s+(-|--)', command):
        yield PolicyHelper.deny(
            "By policy, mv with options/flags is not allowed.\n"
            "Use plain `mv` without any flags (e.g., `mv file.txt newname.txt` or `mv file.txt subdir/file.txt`)."
        )

    # Check path safety using common heuristic
    is_safe, reason = path_in_command_appears_safe(command, "mv")
    if not is_safe:
        yield PolicyHelper.deny(
            f"By policy, mv with {reason}.\n"
            "Use relative paths only (e.g., `mv file.txt newname.txt` or `mv file.txt subdir/file.txt`).\n"
            "If you need to move files upward, first `cd` to the target directory."
        )

    # Allow all other mv operations
    yield PolicyHelper.allow()