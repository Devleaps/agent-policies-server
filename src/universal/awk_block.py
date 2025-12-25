"""Blocks all awk commands for security."""

import re
from typing import Optional
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def awk_block_rule(input_data: ToolUseEvent):
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Block all awk commands
    if re.match(r'^awk\s+', command) or re.match(r'^awk$', command):
        yield PolicyHelper.deny(
            "By policy, awk commands are not allowed for security reasons."
        )