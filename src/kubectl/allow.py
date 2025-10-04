"""Allows only read-only kubectl commands."""

import re
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def kubectl_read_only_rule(input_data: ToolUseEvent):
    # Only process bash tool events
    if not input_data.tool_is_bash:
        return

    # Only process kubectl commands
    if not input_data.command:
        return

    command = input_data.command.strip()

    # Match kubectl or k commands
    if not re.match(r'^(kubectl|k)(?:\s|$)', command):
        return

    # Allowed read-only operations
    allowed_ops = [
        'get', 'list', 'describe', 'logs', 'top', 'version',
        'api-versions', 'api-resources', 'explain', 'cluster-info',
        'config view', 'auth can-i'
    ]

    # Check if any allowed operation is in the command
    for op in allowed_ops:
        if re.search(rf'\b{re.escape(op)}\b', command):
            yield PolicyHelper.allow()
            return

    # Deny all other kubectl operations
    yield PolicyHelper.deny("Only read-only kubectl operations are allowed")