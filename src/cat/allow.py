"""
Cat (concatenate/display) policy rule for safe file operations.

This rule allows cat commands on safe paths only.
"""

import re
from typing import Optional
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper
from src.utils.heuristics import path_appears_safe


def cat_safe_operations_rule(input_data: ToolUseEvent):
    """Allows cat operations on safe paths only."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Match cat commands
    if not re.match(r'^cat\s+', command):
        return

    # Check path safety using common heuristic
    is_safe, reason = path_appears_safe(command)
    if not is_safe:
        yield PolicyHelper.deny(
            f"By policy, cat with {reason}.\n"
            "Use relative paths only (e.g., `cat file.txt` or `cat subdir/file.txt`).\n"
            "If you need to read files upward, first `cd` to the target directory."
        )

    # Allow all other cat operations
    yield PolicyHelper.allow()