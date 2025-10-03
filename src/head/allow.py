"""
Head command policy rule.

This rule allows head commands with any options on safe paths.
"""

import re
from devleaps.policies.server.common.models import ToolUseEvent
from src.heuristics import path_appears_safe
from src.utils import PolicyHelper


def head_allow_rule(input_data: ToolUseEvent):
    """Allows head commands with any options on safe paths."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Match head commands
    if not re.match(r'^head(?:\s|$)', command):
        return

    # Check path safety using common heuristic
    is_safe, reason = path_appears_safe(command)
    if not is_safe:
        yield PolicyHelper.deny(
            f"By policy, head with {reason}.\n"
            "Use relative paths only (e.g., `head file.txt`, `head -n 10 subdir/file.txt`).\n"
            "If you need to read files upward, first `cd` to the target directory."
        )
        return

    # Allow all other safe head operations
    yield PolicyHelper.allow()