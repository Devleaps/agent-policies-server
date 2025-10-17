"""Allows pip show command for inspecting dependencies."""

import re
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def pip_show_rule(input_data: ToolUseEvent):
    """Allow pip show {dependency} for dependency inspection."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Match pip show commands
    if re.match(r'^pip\s+show\s+[\w\-@/\.]+', command):
        yield PolicyHelper.allow()
        return

    return None
