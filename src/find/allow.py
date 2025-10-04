"""Allows find commands with safe paths only."""

import re
from typing import Optional
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper, path_appears_safe


def find_safe_operations_rule(input_data: ToolUseEvent):
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Match find commands
    if not re.match(r'^find\s+', command):
        return

    # Block if already handled by exec rule (has -exec)
    if re.search(r'-exec', command):
        return

    # Check path safety using common heuristic
    is_safe, reason = path_appears_safe(command)
    if not is_safe:
        yield PolicyHelper.deny(
            f"By policy, find with {reason}.\n"
            "Use relative paths only (e.g., `find . -name \"*.txt\"` or `find subdir -type f`).\n"
            "If you need to search upward, first `cd` to the target directory."
        )

    # Allow all other find operations
    yield PolicyHelper.allow()