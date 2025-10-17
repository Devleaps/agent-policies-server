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
    """Allow uv run black/ruff/mypy."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    tools = ['black', 'ruff', 'mypy']

    for tool in tools:
        if re.match(rf'^uv\s+run\s+{tool}\s+', command):
            yield PolicyHelper.allow()


def uv_pytest_allow_rule(input_data: ToolUseEvent):
    """Allow pytest and uv run pytest."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    if re.match(r'^(pytest|uv\s+run\s+pytest)\s+', command) or command in ('pytest', 'uv run pytest'):
        yield PolicyHelper.allow()
