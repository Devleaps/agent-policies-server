"""Strips 'timeout {digit}' prefix to allow underlying command evaluation."""

import re
from devleaps.policies.server.common.models import ToolUseEvent
from dataclasses import replace


def strip_timeout_prefix_middleware(input_data: ToolUseEvent):
    # Only process bash tool events
    if not input_data.tool_is_bash:
        yield input_data
        return

    # Get the command
    command = input_data.command

    if not command:
        yield input_data
        return

    # Strip 'timeout {digit}' prefix (with optional flags and units)
    # Matches: timeout 5, timeout -s KILL 10, timeout 30s, etc.
    if re.match(r'^timeout\s+', command):
        # Remove 'timeout' and any flags/duration
        # Pattern: timeout [flags] {digit}[unit] command
        stripped_command = re.sub(r'^timeout\s+(?:-[a-zA-Z]\s+\S+\s+)*\d+[smhd]?\s+', '', command)

        # Create a new event with the stripped command
        yield replace(input_data, command=stripped_command)
    else:
        # No 'timeout' prefix, pass through
        yield input_data


all_middleware = [strip_timeout_prefix_middleware]
