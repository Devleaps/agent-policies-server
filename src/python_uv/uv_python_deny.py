"""Deny direct python execution and uv run python."""

import re
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def uv_python_direct_deny_rule(input_data: ToolUseEvent):
    """Deny direct python execution - must use uv run python."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    if re.match(r'^python(\d+(\.\d+)?)?\s+', command):
        yield PolicyHelper.deny(
            "Direct python execution not allowed. Use 'uv run python' instead.\n"
            "Example: uv run python script.py"
        )


def uv_python_run_escape_deny_rule(input_data: ToolUseEvent):
    """Deny uv run python - escape hatch for arbitrary code execution."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    if re.match(r'^uv\s+run\s+python(\d+(\.\d+)?)?\s+', command):
        yield PolicyHelper.deny(
            "Direct python execution not allowed, even via uv run.\n"
            "Use pytest for tests, place scripts in files for review."
        )
