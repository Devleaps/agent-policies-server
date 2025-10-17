"""Allows only exact venv creation commands (venv or .venv)."""

import re
from typing import Optional
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def python3_venv_rule(input_data: ToolUseEvent):
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Match python3 -m venv commands
    if not re.match(r'^python3\s+-m\s+venv\s+', command):
        return

    # Allow only exact commands for standard venv directories
    if command == "python3 -m venv venv" or command == "python3 -m venv .venv":
        yield PolicyHelper.allow()
        return

    # Deny all other python3 -m venv commands
    yield PolicyHelper.deny(
        "By policy, only the exact commands are allowed:\n"
        "- `python3 -m venv venv`\n"
        "- `python3 -m venv .venv`\n"
        "No other directory names or options are permitted."
    )