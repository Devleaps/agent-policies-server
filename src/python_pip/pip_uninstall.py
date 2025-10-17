"""Allows uninstalling any Python package."""

import re
from typing import Optional
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def pip_uninstall_rule(input_data: ToolUseEvent):
    if not input_data.tool_is_bash:
        return

    match = re.match(r'pip3?\s+uninstall\s+([\w\-\.\[\]]+(?:\s+[\w\-\.\[\]]+)*)', input_data.command)
    if match:
        package = match.group(1)
        yield PolicyHelper.allow()

    return None