"""Allows rmdir with safe paths only (blocks absolute paths and upward traversal)."""

import re
from typing import Optional
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper, path_appears_safe


def rmdir_safe_operations_rule(input_data: ToolUseEvent):
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Match rmdir commands
    if not re.match(r'^rmdir\s+', command):
        return

    # Block rmdir with options/flags
    if re.search(r'^rmdir\s+(-|--)', command):
        yield PolicyHelper.deny(
            "By policy, rmdir with options/flags is not allowed.\n"
            "Use plain `rmdir` without any flags (e.g., `rmdir emptydir`).\n"
            "On macOS, consider using `trash` command for safer directory deletion."
        )

    # Check path safety using common heuristic
    is_safe, reason = path_appears_safe(command)
    if not is_safe:
        yield PolicyHelper.deny(
            f"By policy, rmdir with {reason}.\n"
            "Use relative paths only (e.g., `rmdir emptydir` or `rmdir subdir/emptydir`).\n"
            "If you need to remove directories upward, first `cd` to the target directory."
        )

    # Allow all other rmdir operations
    yield PolicyHelper.allow()