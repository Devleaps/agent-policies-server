"""
Nslookup policy rule for DNS queries.

This rule allows nslookup commands for DNS resolution.
"""

import re
from typing import Optional
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def nslookup_rule(input_data: ToolUseEvent):
    """Allows nslookup commands."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Allow nslookup
    if command.startswith("nslookup"):
        yield PolicyHelper.allow()

    return None