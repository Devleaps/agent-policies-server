"""Middleware to strip 'git -C {safe_path}' prefix to allow underlying git command evaluation."""

import re
from devleaps.policies.server.common.models import ToolUseEvent
from dataclasses import replace
from src.utils import path_appears_safe


def strip_git_c_prefix_middleware(input_data: ToolUseEvent):
    """Strip 'git -C {safe_path}' prefix to expose underlying git command for policy evaluation."""
    # Only process bash tool events
    if not input_data.tool_is_bash:
        yield input_data
        return

    command = input_data.command.strip()

    if not command:
        yield input_data
        return

    # Match git -C {path} pattern
    # Pattern: git -C /path/to/dir command
    match = re.match(r'^git\s+-C\s+(\S+)(?:\s+(.+))?$', command)

    if match:
        path = match.group(1)
        git_command = match.group(2) or ""

        # Check if path is safe
        is_safe, _ = path_appears_safe(path)
        if not is_safe:
            # Path is unsafe, don't strip - let the policy handle the error
            yield input_data
            return

        # Path is safe, strip the -C {path} part and yield underlying git command
        if git_command:
            stripped_command = f"git {git_command}"
            yield replace(input_data, command=stripped_command)
        else:
            # Just 'git -C {path}' with no command
            yield input_data
    else:
        # No git -C pattern, pass through
        yield input_data


all_middleware = [strip_git_c_prefix_middleware]
