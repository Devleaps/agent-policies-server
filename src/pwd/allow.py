"""
Pwd (print working directory) policy rule.

This rule allows pwd commands to check current directory.
"""

import re
from typing import Optional
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def pwd_allow_rule(input_data: ToolUseEvent):
    """Allows pwd commands."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Allow pwd command
    if re.match(r'^pwd(?:\s|$)', command):
        yield PolicyHelper.allow()