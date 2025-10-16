"""Mypy type checker policy - allow type checking operations."""

import re
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def mypy_check_rule(input_data: ToolUseEvent):
    """Allow mypy for type checking."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Match: mypy .
    if re.match(r'^mypy\s+\.(?:\s|$)', command):
        yield PolicyHelper.allow()
        return

    # Match: mypy {file or directory}
    if re.match(r'^mypy\s+[\w\-./]+(?:\s|$)', command):
        yield PolicyHelper.allow()
        return

    return None
