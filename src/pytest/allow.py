"""
Pytest execution policy rule.

This rule explicitly allows pytest commands for proper test execution.
"""

from typing import Optional
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def pytest_rule(input_data: ToolUseEvent):
    """Allows pytest commands."""
    if not input_data.tool_is_bash:
        return

    if input_data.command.strip().startswith("pytest"):
        yield PolicyHelper.allow()

    return None