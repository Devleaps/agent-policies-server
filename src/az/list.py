"""
Azure CLI policy rule for allowing safe list commands.

This rule whitelists Azure CLI list commands that are read-only operations.
"""

import re
from typing import Optional
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def azure_cli_list_rule(input_data: ToolUseEvent):
    """Allows Azure CLI list commands (az [word] list, az [word] [word] list)."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command

    # Match Azure CLI list commands:
    # - az {word} list
    # - az {word} {word} list
    # Allows any number of subcommands between az and list
    if re.match(r'^az\s+(?:[a-z0-9\-]+\s+)+list(?:\s|$)', command):
        yield PolicyHelper.allow()

    return None