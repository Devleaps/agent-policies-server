"""Allows all git show command variants."""

import re
from typing import Optional
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def git_show_rule(input_data: ToolUseEvent):
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Allow git show (with any options and arguments)
    if re.match(r'^git\s+show(?:\s|$)', command):
        yield PolicyHelper.allow()

    return None