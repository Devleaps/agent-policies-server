"""
Tflint policy rule for Terraform linting.

This rule allows tflint commands for Terraform code analysis.
"""

from typing import Optional
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def tflint_rule(input_data: ToolUseEvent):
    """Allows tflint commands."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Allow tflint
    if command.startswith("tflint"):
        yield PolicyHelper.allow()

    return None