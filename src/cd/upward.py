"""
CD (change directory) policy rule for upward navigation.

This rule allows cd commands that only use upward navigation patterns.
"""

import re
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def cd_upward_navigation_rule(input_data: ToolUseEvent):
    """Allows cd operations that only navigate upward using / and . characters."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Match cd commands
    if not re.match(r'^cd\s+', command):
        return

    # Extract the path argument after cd
    match = re.match(r'^cd\s+(.+)$', command)
    if not match:
        return

    path = match.group(1).strip()

    # Allow paths that only contain /, ., and no other characters
    # This includes patterns like: .., ../..
    if re.match(r'^[/.]*$', path) and path:
        yield PolicyHelper.allow()
        return

    # If it doesn't match upward navigation pattern, let other rules handle it
    return