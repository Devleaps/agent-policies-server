"""
Diff policy rule for safe file operations.

This rule allows diff commands on safe paths only.
"""

import re
from typing import Optional
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper
from src.heuristics import path_appears_safe


def diff_safe_operations_rule(input_data: ToolUseEvent):
    """Allows diff operations on safe paths only."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Match diff commands
    if not re.match(r'^diff\s+', command):
        return

    # Check path safety using common heuristic
    is_safe, reason = path_appears_safe(command)
    if not is_safe:
        yield PolicyHelper.deny(
            f"By policy, diff with {reason}.\n"
            "Use relative paths only (e.g., `diff file1.txt file2.txt` or `diff dir1/file.txt dir2/file.txt`).\n"
            "If you need to compare files upward, first `cd` to the target directory."
        )

    # Allow all other diff operations
    yield PolicyHelper.allow()