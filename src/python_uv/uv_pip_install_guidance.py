"""Guidance for uv pip install usage."""

import re
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def uv_pip_install_guidance_rule(input_data: ToolUseEvent):
    """Suggest uv add when uv pip install is used."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    if re.match(r'^uv\s+pip\s+install\s+', command):
        yield PolicyHelper.allow()
        yield PolicyHelper.guidance(
            "Consider using `uv add` instead of `uv pip install` for better dependency management.\n"
            "Example: `uv add package-name`"
        )
