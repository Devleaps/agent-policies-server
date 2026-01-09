"""Block absolute path executables and .venv/bin executables."""

import re
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def absolute_path_executable_rule(input_data: ToolUseEvent):
    """Block commands that use absolute paths or .venv/bin executables."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Check for absolute path (starts with /)
    if re.match(r'^/', command):
        yield PolicyHelper.deny(
            "Absolute path executables are not allowed.\n"
            "Use relative paths or command names directly (e.g., `pytest` instead of `/path/to/pytest`)."
        )
        return

    # Check for .venv/bin usage
    if re.match(r'^\.venv/bin/', command):
        yield PolicyHelper.deny(
            "Direct execution from `.venv/bin/` is not allowed.\n"
            "Use `uv run` instead (e.g., `uv run pytest` instead of `.venv/bin/pytest`)."
        )
        return
