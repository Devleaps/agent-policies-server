"""
Sleep policy rule for safe operations.

This rule allows sleep commands with durations at or below 60 seconds.
"""

import re
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def sleep_duration_rule(input_data: ToolUseEvent):
    """Allows sleep commands with duration <= 60 seconds."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Match sleep commands with a number
    sleep_match = re.match(r'^sleep\s+(\d+(?:\.\d+)?)', command)
    if not sleep_match:
        return

    duration = float(sleep_match.group(1))

    if duration > 60:
        yield PolicyHelper.deny(
            "By policy, sleep durations above 60 seconds are not allowed.\n"
            "Use a duration of 60 seconds or less (e.g., `sleep 30`, `sleep 60`)."
        )
    else:
        yield PolicyHelper.allow()