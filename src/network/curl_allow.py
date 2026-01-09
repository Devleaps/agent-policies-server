"""Allows curl commands to localhost and policy server endpoints only."""

import re
from typing import Optional
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper, url_is_localhost


# Allowed external endpoints
ALLOWED_EXTERNAL_DOMAINS = [
    "agent-policies.dev.devleaps.nl",
    "agent-policies.devleaps.nl",
]


def url_is_allowed_external(url: str) -> bool:
    """Check if URL is an allowed external endpoint."""
    return any(domain in url for domain in ALLOWED_EXTERNAL_DOMAINS)


def curl_localhost_rule(input_data: ToolUseEvent):
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Match curl commands
    if not re.match(r'^curl\s+', command):
        return

    # Extract URL from curl command - find any word containing localhost, 127., or ::1
    words = command.split()

    # Check each word to see if it contains a localhost or allowed external URL
    for word in words:
        if url_is_localhost(word) or url_is_allowed_external(word):
            yield PolicyHelper.allow()
            return

    # No allowed URL found
    yield PolicyHelper.deny(
        "By policy, curl is only allowed to localhost or policy server endpoints.\n"
        "Use localhost, 127.0.0.1, ::1, or agent-policies.*.devleaps.nl"
    )