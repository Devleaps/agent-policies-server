"""Terragrunt policies allowing only safe read-only and planning operations."""

import re
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def terragrunt_plan_rule(input_data: ToolUseEvent):
    """Allow terragrunt plan for dry-run execution planning."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Match terragrunt plan commands
    if re.match(r'^terragrunt\s+plan(?:\s|$)', command):
        yield PolicyHelper.allow()
        return

    return None


def terragrunt_default_block_rule(input_data: ToolUseEvent):
    """Block all terragrunt commands except plan (destructive operations)."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Check if this is a terragrunt command
    if not command.startswith('terragrunt '):
        return None

    # Allow if command contains 'plan'
    if ' plan' in command:
        return None  # Let other rules handle it

    # Block all other terragrunt commands (apply, destroy, etc.)
    yield PolicyHelper.deny(
        "Terragrunt command blocked by default policy. "
        "Only 'plan' (dry-run) commands are allowed. "
        "Destructive operations like 'apply' and 'destroy' are not permitted."
    )
