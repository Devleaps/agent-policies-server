"""pip-audit security auditing policy - allow security checks."""

import re
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def pip_audit_rule(input_data: ToolUseEvent):
    """Allow pip-audit for security vulnerability scanning."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Match: pip-audit
    if re.match(r'^pip-audit(?:\s|$)', command):
        yield PolicyHelper.allow()
        return

    return None
