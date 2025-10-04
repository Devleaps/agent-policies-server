"""Splits chained commands (&&, |) for independent evaluation."""

import re
from devleaps.policies.server.common.models import ToolUseEvent
from dataclasses import replace


def split_commands_middleware(input_data: ToolUseEvent):
    # Only process bash tool events
    if not input_data.tool_is_bash:
        yield input_data
        return

    # Get the command
    command = input_data.command

    if not command:
        yield input_data
        return

    # First split on ' && ' if present
    if ' && ' in command:
        commands = [cmd.strip() for cmd in command.split(' && ') if cmd.strip()]
    else:
        commands = [command]

    # Then split each command on ' | ' (pipe)
    all_commands = []
    for cmd in commands:
        if ' | ' in cmd:
            pipe_parts = [part.strip() for part in cmd.split(' | ') if part.strip()]
            all_commands.extend(pipe_parts)
        else:
            all_commands.append(cmd)

    # If we have multiple commands, yield each separately
    if len(all_commands) > 1:
        for cmd in all_commands:
            # Create a new event for each split command using dataclass replace
            split_input = replace(input_data, command=cmd)
            yield split_input
    else:
        # Single command, pass through
        yield input_data