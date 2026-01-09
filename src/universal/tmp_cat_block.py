"""Blocks cat heredoc writes to /tmp/ directory."""

import re
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def tmp_cat_block_rule(input_data: ToolUseEvent):
    """Block cat commands that write to /tmp/ directory."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Check if command starts with cat
    if not re.match(r'^cat\s+', command):
        return

    # Check for redirect to /tmp/ (> or >>)
    if re.search(r'>\s*/tmp/', command):
        yield PolicyHelper.deny(
            "Writing to `/tmp/` with `cat` is not allowed.\n"
            "Use workspace-relative paths for temporary files instead."
        )
