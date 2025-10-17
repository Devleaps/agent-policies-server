"""Deny uv add."""

import re
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def uv_add_deny_rule(input_data: ToolUseEvent):
    """Deny uv add - use uv sync from lock file instead."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    if re.match(r'^uv\s+add\s+', command):
        yield PolicyHelper.deny(
            "Adding new dependencies not allowed.\n"
            "Use 'uv sync' to install from lock file instead."
        )
