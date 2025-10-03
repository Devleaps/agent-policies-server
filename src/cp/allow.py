"""
Cp (copy) policy rule for safe file operations.

This rule blocks absolute paths and upward directory traversals in cp commands.
"""

import re
from typing import Optional
from devleaps.policies.server.common.models import ToolUseEvent
from src.heuristics import path_appears_safe
from src.utils import PolicyHelper


def cp_safe_operations_rule(input_data: ToolUseEvent):
    """Allows cp operations with or without options on safe paths only."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Match cp commands
    if not re.match(r'^cp\s+', command):
        return

    # Check path safety using common heuristic
    is_safe, reason = path_appears_safe(command)
    if not is_safe:
        yield PolicyHelper.deny(
            f"By policy, cp with {reason}.\n"
            "Use relative paths only (e.g., `cp file.txt backup.txt` or `cp -r dir1 dir2`).\n"
            "If you need to copy files upward, first `cd` to the target directory."
        )
        return

    # Allow all cp operations with safe paths (with or without options)
    yield PolicyHelper.allow()