"""Blocks find commands with -exec flag for security."""

import re
from typing import Optional
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def find_exec_rule(input_data: ToolUseEvent):
    if not input_data.tool_is_bash:
        return

    if re.search(r'\bfind\b.*-exec', input_data.command):
        yield PolicyHelper.deny(
            "find commands with -exec are not allowed for security reasons"
        )