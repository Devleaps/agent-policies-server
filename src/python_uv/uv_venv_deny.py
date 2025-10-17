"""Deny direct venv creation."""

import re
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def uv_venv_deny_rule(input_data: ToolUseEvent):
    """Deny python -m venv - uv handles environment management."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    if re.match(r'^python(\d+(\.\d+)?)?\s+-m\s+venv\b', command):
        yield PolicyHelper.deny(
            "Direct venv creation not allowed.\n"
            "UV manages environments automatically - use 'uv sync' instead."
        )
