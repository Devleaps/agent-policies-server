"""Allows Azure CLI show commands (read-only operations)."""

import re
from typing import Optional
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def azure_cli_show_rule(input_data: ToolUseEvent):
    if not input_data.tool_is_bash:
        return

    command = input_data.command

    # Match Azure CLI show commands:
    # - az {word} show
    # - az {word} {word} show
    # Allows any number of subcommands between az and show
    if re.match(r'^az\s+(?:[a-z0-9\-]+\s+)+show(?:\s|$)', command):
        yield PolicyHelper.allow()

    return None