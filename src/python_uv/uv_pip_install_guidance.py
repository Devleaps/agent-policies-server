"""Deny uv pip install usage."""

import re
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def uv_pip_install_deny_rule(input_data: ToolUseEvent):
    """Deny uv pip install and suggest uv add instead."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    if re.match(r'^uv\s+pip\s+install\s+', command):
        yield PolicyHelper.deny(
            "`uv pip install` is not allowed. Use `uv add` instead for better dependency management.\n"
            "Example: `uv add package-name`"
        )
