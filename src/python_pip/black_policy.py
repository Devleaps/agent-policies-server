"""Black code formatter policy - allow formatting operations."""

import re
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def black_format_rule(input_data: ToolUseEvent):
    """Allow black for code formatting."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Match: black .
    if re.match(r'^black\s+\.(?:\s|$)', command):
        yield PolicyHelper.allow()
        return

    # Match: black {file or directory}
    if re.match(r'^black\s+[\w\-./]+(?:\s|$)', command):
        yield PolicyHelper.allow()
        return

    return None
