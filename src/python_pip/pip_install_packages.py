"""Enforces whitelist of allowed packages for pip install."""

import re
from typing import Optional
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def pip_install_packages_rule(input_data: ToolUseEvent):
    if not input_data.tool_is_bash:
        return

    # Skip if this is a requirements.txt install (handled by other rule)
    if "-r requirements.txt" in input_data.command:
        return

    if not re.match(r'pip3?\s+install\s+', input_data.command):
        return

    allowed_packages = {
        "requests", "fastapi", "uvicorn[standard]", "pydantic", "pytest",
        "uvicorn", "httpx"
    }

    # Extract package names, ignoring version specs and extras
    packages = re.findall(r'(?:^|\s)([a-zA-Z0-9][\w\-]*(?:\[[^\]]+\])?)', input_data.command[12:])

    for pkg in packages:
        if pkg not in allowed_packages:
            yield PolicyHelper.deny(
                f"By policy, the package '{pkg}' is not allowed to be installed.\n"
                f"Allowed packages are: {', '.join(sorted(allowed_packages))}\n"
                "If the allowed list is insufficient, please refer back to the user for approval."
            )

    yield PolicyHelper.allow()