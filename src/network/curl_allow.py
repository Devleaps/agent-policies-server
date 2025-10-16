"""Allows curl commands to localhost only."""

import re
from typing import Optional
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper, url_is_localhost


def curl_localhost_rule(input_data: ToolUseEvent):
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Match curl commands
    if not re.match(r'^curl\s+', command):
        return

    # Check if command contains a localhost URL
    if url_is_localhost(command):
        yield PolicyHelper.allow()
    else:
        # Deny all other curl commands
        yield PolicyHelper.deny(
            "By policy, curl is only allowed to localhost.\n"
            "Use localhost, 127.0.0.1, or ::1 (e.g., `curl localhost:8000` or `curl 127.0.0.1:3000`)."
        )