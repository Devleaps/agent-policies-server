"""
Mv (move/rename) policy rule for safe file operations.

This rule blocks absolute paths and upward directory traversals in mv commands.
"""

import re
from typing import Optional
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils.heuristics import path_appears_safe
from src.utils import PolicyHelper


def mv_safe_operations_rule(input_data: ToolUseEvent):
    """Blocks mv operations with options, absolute paths or upward directory traversals."""
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
    is_safe, reason = path_appears_safe(command)
    if not is_safe:
        yield PolicyHelper.deny(
            f"By policy, mv with {reason}.\n"
            "Use relative paths only (e.g., `mv file.txt newname.txt` or `mv file.txt subdir/file.txt`).\n"
            "If you need to move files upward, first `cd` to the target directory."
        )

    # Allow all other mv operations
    yield PolicyHelper.allow()