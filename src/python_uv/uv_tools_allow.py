"""Allow uv sync, pytest, and uv run tools."""

import re
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def uv_sync_allow_rule(input_data: ToolUseEvent):
    """Allow uv sync - safe environment setup from lock file."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    if re.match(r'^uv\s+sync\b', command):
        yield PolicyHelper.allow()


def uv_tools_run_allow_rule(input_data: ToolUseEvent):
    """Allow uv run black/ruff/mypy/pytest."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    tools = ['black', 'ruff', 'mypy', 'pytest']

    for tool in tools:
        if re.match(rf'^uv\s+run\s+{tool}\s+', command):
            yield PolicyHelper.allow()
        # Also match command without arguments (e.g., "uv run pytest")
        if command == f'uv run {tool}':
            yield PolicyHelper.allow()
