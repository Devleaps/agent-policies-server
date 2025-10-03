"""
Terragrunt policy rules for safe operations.

This rule allows safe terragrunt commands like plan.
"""

import re
from typing import Optional
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def terragrunt_rule(input_data: ToolUseEvent):
    """Allows safe terragrunt commands."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Allow terragrunt plan
    if re.match(r'^terragrunt\s+plan(?:\s|$)', command):
        yield PolicyHelper.allow()

    return None