"""Allows rm with safe paths only (blocks absolute paths and upward traversal)."""

import re
from typing import Optional
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper, path_appears_safe


def rm_safe_operations_rule(input_data: ToolUseEvent):
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Match rm commands
    if not re.match(r'^rm\s+', command):
        return

    # Block rm with options/flags
    if re.search(r'^rm\s+(-|--)', command):
        yield PolicyHelper.deny(
            "By policy, rm with options/flags is not allowed.\n"
            "Use plain `rm` without any flags (e.g., `rm file.txt` or `rm subdir/file.txt`).\n"
            "On macOS, consider using `trash` command for safer file deletion."
        )

    # Check path safety using common heuristic
    is_safe, reason = path_appears_safe(command)
    if not is_safe:
        yield PolicyHelper.deny(
            f"By policy, rm with {reason}.\n"
            "Use relative paths only (e.g., `rm file.txt` or `rm subdir/file.txt`).\n"
            "If you need to remove files upward, first `cd` to the target directory."
        )

    # Allow all other rm operations
    yield PolicyHelper.allow()
