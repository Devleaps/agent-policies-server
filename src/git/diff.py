"""
Git diff policy rule.

This rule allows git diff commands with safe paths.
"""

import re
from typing import Optional
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper
from src.heuristics import path_appears_safe


def git_diff_rule(input_data: ToolUseEvent):
    """Allows safe git diff operations."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Allow git diff (with common patterns)
    if re.match(r'^git\s+diff(?:\s|$)', command):
        # Check path safety if paths are specified
        is_safe, reason = path_appears_safe(command)
        if not is_safe:
            yield PolicyHelper.deny(
                f"By policy, git diff with {reason}.\n"
                "Use relative paths only (e.g., `git diff`, `git diff file.txt`, `git diff HEAD~1`).\n"
                "If you need to diff files upward, first `cd` to the target directory."
            )

        yield PolicyHelper.allow()

    return None