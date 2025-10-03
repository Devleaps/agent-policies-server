"""
Virtual environment activation policy rule.

This rule allows activation of Python virtual environments.
"""

from typing import Optional
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def venv_activation_rule(input_data: ToolUseEvent):
    """Allows virtual environment activation."""
    if not input_data.tool_is_bash:
        return

    if input_data.command.strip() == "source venv/bin/activate":
        yield PolicyHelper.allow()

    return None