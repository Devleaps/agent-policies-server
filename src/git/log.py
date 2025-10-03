"""
Git log policy rule.

This rule allows all git log command variants.
"""

import re
from typing import Optional
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def git_log_rule(input_data: ToolUseEvent):
    """Allows all git log commands and variants."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Allow git log (with any options and arguments)
    if re.match(r'^git\s+log(?:\s|$)', command):
        yield PolicyHelper.allow()

    return None