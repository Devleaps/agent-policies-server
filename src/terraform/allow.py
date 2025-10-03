"""
Terraform policy rules for safe operations.

This rule allows safe terraform commands like fmt and plan.
"""

import re
from typing import Optional
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def terraform_rule(input_data: ToolUseEvent):
    """Allows safe terraform commands, blocks destructive operations."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Block terraform apply (destructive operation)
    if re.match(r'^terraform\s+apply(?:\s|$)', command):
        yield PolicyHelper.deny(
            "By policy, terraform apply is not allowed.\n"
            "Use `terraform plan` to review changes without applying them."
        )

    # Allow terraform fmt
    if re.match(r'^terraform\s+fmt(?:\s+[\w\-\.\/]+)?(?:\s|$)', command):
        yield PolicyHelper.allow()

    # Allow terraform plan
    if re.match(r'^terraform\s+plan(?:\s|$)', command):
        yield PolicyHelper.allow()