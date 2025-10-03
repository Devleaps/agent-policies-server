"""
Yarn package manager policy rules for safe operations.

This rule allows safe yarn commands like test, start, remove, why, and build.
"""

import re
from typing import Optional
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def yarn_safe_commands_rule(input_data: ToolUseEvent):
    """Allows safe yarn commands."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Allow yarn test
    if re.match(r'^yarn\s+test(?:\s|$)', command):
        yield PolicyHelper.allow()

    # Allow yarn start
    if re.match(r'^yarn\s+start(?:\s|$)', command):
        yield PolicyHelper.allow()

    # Allow yarn remove
    if re.match(r'^yarn\s+remove\s+', command):
        yield PolicyHelper.allow()

    # Allow yarn why {word}
    if re.match(r'^yarn\s+why\s+[\w\-@/]+(?:\s|$)', command):
        yield PolicyHelper.allow()

    # Allow yarn build
    if re.match(r'^yarn\s+build(?:\s|$)', command):
        yield PolicyHelper.allow()

    return None