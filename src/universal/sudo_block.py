"""Blocks all sudo commands for security (privilege escalation)."""

import re
from typing import Optional
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def sudo_block_rule(input_data: ToolUseEvent):
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Block all sudo commands
    if re.match(r'^sudo\s+', command):
        yield PolicyHelper.deny(
            "By policy, sudo commands are not allowed for security reasons.\n"
            "Run commands without sudo privileges or configure appropriate permissions."
        )