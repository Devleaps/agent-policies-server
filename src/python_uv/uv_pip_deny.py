"""Deny direct pip and uv run pip."""

import re
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def uv_pip_direct_deny_rule(input_data: ToolUseEvent):
    """Deny direct pip - must use uv sync or uv add."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    if re.match(r'^pip(\d+(\.\d+)?)?\s+', command):
        yield PolicyHelper.deny(
            "Direct `pip` usage is not allowed.\n"
            "To add dependencies: use `uv add package-name` (has integrated whitelist).\n"
            "To sync existing dependencies: use `uv sync`.\n"
            "Example: `uv add requests`"
        )


def uv_pip_run_deny_rule(input_data: ToolUseEvent):
    """Deny uv run pip - use uv add or uv sync instead."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    if re.match(r'^uv\s+run\s+pip\s+', command):
        yield PolicyHelper.deny(
            "Arbitrary `pip` installation not allowed via `uv run`.\n"
            "To add dependencies: use `uv add package-name` (has integrated whitelist).\n"
            "To sync existing dependencies: use `uv sync`.\n"
            "Example: `uv add requests`"
        )
