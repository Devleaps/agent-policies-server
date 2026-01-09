"""Deny direct python execution and uv run python."""

import re
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def uv_python_direct_deny_rule(input_data: ToolUseEvent):
    """Deny direct python execution - must use uv run."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    if not re.match(r'^python(\d+(\.\d+)?)?\s+', command):
        return

    # Check for python -m {module} pattern - suggest uv run {module}
    module_match = re.match(r'^python(\d+(\.\d+)?)?\s+-m\s+(\S+)', command)
    if module_match:
        module_name = module_match.group(3)
        yield PolicyHelper.deny(
            f"Direct python execution not allowed. Use `uv run {module_name}` instead."
        )
        return

    # Check for scripts/ folder - ask user for confirmation
    if re.search(r'\sscripts/', command):
        yield PolicyHelper.ask()
        return

    # Extract script path for better guidance
    script_match = re.match(r'^python(\d+(\.\d+)?)?\s+(\S+)', command)
    if script_match:
        script_path = script_match.group(3)
        yield PolicyHelper.deny(
            f"Direct python execution not allowed. Use `uv run {script_path}` instead,\n"
            "or move the script to a `scripts/` folder for user review."
        )
        return

    yield PolicyHelper.deny(
        "Direct python execution not allowed. Use `uv run` instead."
    )


def uv_python_run_escape_deny_rule(input_data: ToolUseEvent):
    """Deny uv run python - escape hatch for arbitrary code execution."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    if re.match(r'^uv\s+run\s+python(\d+(\.\d+)?)?\s+', command):
        yield PolicyHelper.deny(
            "Direct python execution not allowed, even via uv run.\n"
            "Use `pytest` for tests, or place scripts in `scripts/` folder for user review."
        )
