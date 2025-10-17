"""Ruff linter and formatter policy - allow check and format operations."""

import re
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def ruff_check_rule(input_data: ToolUseEvent):
    """Allow ruff check for linting."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Match: ruff check
    if re.match(r'^ruff\s+check(?:\s|$)', command):
        yield PolicyHelper.allow()
        return

    return None


def ruff_format_rule(input_data: ToolUseEvent):
    """Allow ruff format for code formatting."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Match: ruff format
    if re.match(r'^ruff\s+format(?:\s|$)', command):
        yield PolicyHelper.allow()
        return

    return None
