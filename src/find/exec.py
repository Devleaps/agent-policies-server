"""
Security rule to deny find commands with -exec flag.

This rule prevents potentially dangerous find commands that can execute arbitrary code.
"""

import re
from typing import Optional
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def find_exec_rule(input_data: ToolUseEvent):
    """Denies find commands with -exec."""
    if not input_data.tool_is_bash:
        return

    if re.search(r'\bfind\b.*-exec', input_data.command):
        yield PolicyHelper.deny(
            "find commands with -exec are not allowed for security reasons"
        )