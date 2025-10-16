"""Pytest with coverage policy - allow coverage reporting."""

import re
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def pytest_cov_rule(input_data: ToolUseEvent):
    """Allow pytest with coverage reporting."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Match: pytest --cov
    if re.match(r'^pytest\s+.*--cov(?:\s|$|=)', command):
        yield PolicyHelper.allow()
        return

    return None
