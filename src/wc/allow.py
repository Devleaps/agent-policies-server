"""
Wc (word count) policy rule for safe file operations.

This rule blocks absolute paths and upward directory traversals in wc commands.
"""

import re
from typing import Optional
from devleaps.policies.server.common.models import ToolUseEvent
from src.heuristics import path_appears_safe
from src.utils import PolicyHelper


def wc_safe_operations_rule(input_data: ToolUseEvent):
    """Allows wc operations with or without options on safe paths only."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Match wc commands
    if not re.match(r'^wc\s+', command):
        return

    # Check path safety using common heuristic
    is_safe, reason = path_appears_safe(command)
    if not is_safe:
        yield PolicyHelper.deny(
            f"By policy, wc with {reason}.\n"
            "Use relative paths only (e.g., `wc file.txt` or `wc -l *.py`).\n"
            "If you need to count files upward, first `cd` to the target directory."
        )
        return

    # Allow all wc operations with safe paths (with or without options)
    yield PolicyHelper.allow()