"""
Curl policy rule for localhost connections.

This rule allows curl commands to localhost only.
"""

import re
from typing import Optional
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def curl_localhost_rule(input_data: ToolUseEvent):
    """Allows curl commands to localhost only."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Match curl commands
    if not re.match(r'^curl\s+', command):
        return

    # Allow curl to localhost variations
    if re.search(r'(localhost|127\.0\.0\.1|::1)', command):
        yield PolicyHelper.allow()
    else:
        # Deny all other curl commands
        yield PolicyHelper.deny(
            "By policy, curl is only allowed to localhost.\n"
            "Use localhost, 127.0.0.1, or ::1 (e.g., `curl localhost:8000` or `curl 127.0.0.1:3000`)."
        )