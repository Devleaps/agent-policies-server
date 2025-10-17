"""Deny direct black/ruff/mypy."""

import re
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def uv_tools_direct_deny_rule(input_data: ToolUseEvent):
    """Deny direct black/ruff/mypy - must use uv run."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    tools = {
        'black': 'uv run black .',
        'ruff': 'uv run ruff check . OR uv run ruff format .',
        'mypy': 'uv run mypy .'
    }

    for tool, usage in tools.items():
        if re.match(rf'^{tool}\s+', command):
            yield PolicyHelper.deny(
                f"{tool.capitalize()} must be run via uv.\n"
                f"Use: {usage}"
            )
