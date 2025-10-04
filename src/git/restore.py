"""Allows git restore commands on safe paths only."""

import re
from typing import Optional
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper, path_appears_safe


def git_restore_rule(input_data: ToolUseEvent):
    """Allows git restore commands on safe paths."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Match git restore commands
    if not re.match(r'^git\s+restore(?:\s|$)', command):
        return

    # Check if paths appear safe
    is_safe, reason = path_appears_safe(command)
    if not is_safe:
        yield PolicyHelper.deny(f"git restore blocked: {reason}")
        return

    # Allow safe git restore commands
    yield PolicyHelper.allow()

    return None