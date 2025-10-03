"""
Azure CLI default block policy rule.

This rule blocks all Azure CLI commands by default unless they contain 'list' or 'show'.
This ensures only read-only operations are allowed by default.
"""

import re
from typing import Optional
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def azure_cli_default_block_rule(input_data: ToolUseEvent):
    """Block Azure CLI commands unless they contain 'list' or 'show'."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command

    # Check if this is an az command
    if not command.startswith('az '):
        return None

    # Allow if command contains 'list' or 'show' anywhere in the command
    if ' list' in command or ' show' in command:
        return None  # Let other rules handle it

    # Block all other az commands
    yield PolicyHelper.deny(
        "Azure CLI command blocked by default policy. "
        "Only 'list' and 'show' commands are allowed for read-only operations."
    )