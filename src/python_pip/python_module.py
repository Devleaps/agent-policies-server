"""Blocks python -m pytest, requires direct pytest usage."""

import re
from typing import Optional
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def python_module_rule(input_data: ToolUseEvent):
    if not input_data.tool_is_bash:
        return

    if re.match(r'python3?\s+-m\s+pytest', input_data.command):
        yield PolicyHelper.deny(
            "By policy, `python -m pytest` have been disallowed.\n"
            "Use `pytest` directly."
        )

    return None