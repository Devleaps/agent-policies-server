"""
LS (list directory) policy rule for safe operations.

This rule allows ls commands with any options on safe paths.
"""

import re
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper
from src.utils.heuristics import path_appears_safe


def ls_allow_rule(input_data: ToolUseEvent):
    """Allows ls commands with any options on safe paths."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Match ls commands
    if not re.match(r'^ls(?:\s|$)', command):
        return

    # Check path safety using common heuristic
    is_safe, reason = path_appears_safe(command)
    if not is_safe:
        yield PolicyHelper.deny(
            f"By policy, ls with {reason}.\n"
            "Use relative paths only (e.g., `ls`, `ls -la`, `ls subdir`).\n"
            "If you need to list upward, first `cd` to the target directory."
        )
        return

    # Allow all other safe ls operations
    yield PolicyHelper.allow()