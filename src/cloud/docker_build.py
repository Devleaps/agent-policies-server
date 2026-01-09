"""Allow docker build with local paths and -t option."""

import re
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def docker_build_rule(input_data: ToolUseEvent):
    """Allow docker build with local context paths and -t tag option."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Match: docker build [options] [context]
    if not re.match(r'^docker\s+build(?:\s|$)', command):
        return

    # Allow docker build (will validate context path is local/relative)
    # Common patterns:
    # - docker build .
    # - docker build -t name .
    # - docker build -t name:tag .
    # - docker build --tag name .

    # Check for absolute paths in context
    if re.search(r'\s+(/[^\s]+)\s*$', command):
        yield PolicyHelper.deny(
            "`docker build` with absolute path context is not allowed.\n"
            "Use relative paths like `.` or `./subdir`"
        )
        return

    # Allow docker build with local paths
    yield PolicyHelper.allow()
