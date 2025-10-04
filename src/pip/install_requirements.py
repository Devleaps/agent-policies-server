"""Allows installation from requirements.txt."""

import re
from typing import Optional
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def pip_install_requirements_rule(input_data: ToolUseEvent):
    if not input_data.tool_is_bash:
        return

    if re.match(r'pip3?\s+install\s+.*-r\s+requirements\.txt', input_data.command):
        yield PolicyHelper.allow()

    return None