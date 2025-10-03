"""
Directory creation policy rules for safe operations.

This rule allows mkdir and mkdir -p commands for creating directories.
"""

import re
from typing import Optional
from devleaps.policies.server.common.models import ToolUseEvent
from src.heuristics import path_appears_safe
from src.utils import PolicyHelper


def mkdir_safe_commands_rule(input_data: ToolUseEvent):
    """Allows safe mkdir commands with path safety checks."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Match mkdir commands (with or without -p)
    if not re.match(r'^mkdir\s+', command):
        return

    # Check path safety using common heuristic
    is_safe, reason = path_appears_safe(command)
    if not is_safe:
        yield PolicyHelper.deny(
            f"By policy, mkdir with {reason}.\n"
            "Use relative paths only (e.g., `mkdir newdir` or `mkdir -p subdir/newdir`).\n"
            "If you need to create directories upward, first `cd` to the target location."
        )

    # Allow mkdir {file}
    if re.match(r'^mkdir\s+[^\s-]', command):
        yield PolicyHelper.allow()

    # Allow mkdir -p {file}
    if re.match(r'^mkdir\s+-p\s+', command):
        yield PolicyHelper.allow()

    return None