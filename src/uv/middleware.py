"""
UV run command middleware for preprocessing inputs.

This middleware strips 'uv run' prefix from commands to allow them to match other policy rules.
"""

import re
from devleaps.policies.server.common.models import ToolUseEvent
from dataclasses import replace


def strip_uv_run_prefix_middleware(input_data: ToolUseEvent):
    """
    Strip 'uv run' prefix from commands.

    Transforms commands like 'uv run pytest' to 'pytest'
    by creating a new event with the stripped command.
    """
    # Only process bash tool events
    if not input_data.tool_is_bash:
        yield input_data
        return

    # Get the command
    command = input_data.command

    if not command:
        yield input_data
        return

    # Strip 'uv run' prefix
    if re.match(r'^uv\s+run\s+', command):
        # Remove 'uv run '
        stripped_command = re.sub(r'^uv\s+run\s+', '', command)

        # Create a new event with the stripped command
        yield replace(input_data, command=stripped_command)
    else:
        # No 'uv run' prefix, pass through
        yield input_data
