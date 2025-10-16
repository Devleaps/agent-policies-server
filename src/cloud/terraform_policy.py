"""Terraform policies allowing only safe read-only and formatting operations."""

import re
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def terraform_fmt_rule(input_data: ToolUseEvent):
    """Allow terraform fmt for code formatting."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Match terraform fmt commands
    if re.match(r'^terraform\s+fmt(?:\s|$)', command):
        yield PolicyHelper.allow()
        return

    return None


def terraform_plan_rule(input_data: ToolUseEvent):
    """Allow terraform plan for dry-run execution planning."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Match terraform plan commands
    if re.match(r'^terraform\s+plan(?:\s|$)', command):
        yield PolicyHelper.allow()
        return

    return None


def terraform_default_block_rule(input_data: ToolUseEvent):
    """Block all terraform commands except fmt and plan (destructive operations)."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Check if this is a terraform command
    if not command.startswith('terraform '):
        return None

    # Allow if command contains 'fmt' or 'plan'
    if ' fmt' in command or ' plan' in command:
        return None  # Let other rules handle it

    # Block all other terraform commands (apply, destroy, etc.)
    yield PolicyHelper.deny(
        "Terraform command blocked by default policy. "
        "Only 'fmt' (formatting) and 'plan' (dry-run) commands are allowed. "
        "Destructive operations like 'apply' and 'destroy' are not permitted."
    )
