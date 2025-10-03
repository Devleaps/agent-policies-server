"""
CD (change directory) policy rule for safe operations.

This rule allows cd commands with safe paths only.
"""

import re
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper
from src.heuristics import path_appears_safe


def cd_safe_operations_rule(input_data: ToolUseEvent):
    """Allows cd operations with safe paths only."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Match cd commands
    if not re.match(r'^cd\s+', command):
        return

    # Extract the path argument after cd
    match = re.match(r'^cd\s+(.+)$', command)
    if not match:
        return

    path = match.group(1).strip()

    # Skip upward navigation patterns - let the upward navigation rule handle them
    if re.match(r'^[/.]*$', path) and path:
        return

    # Check path safety using common heuristic
    is_safe, reason = path_appears_safe(command)
    if not is_safe:
        yield PolicyHelper.deny(
            f"By policy, cd with {reason}.\n"
            "Use relative paths only (e.g., `cd subdir` or `cd project/src`).\n"
            "If you need to navigate upward, use paths like `cd ..` or `cd ../..`."
        )
        return

    # Allow all other safe cd operations
    yield PolicyHelper.allow()