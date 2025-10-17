"""Enforce whitelist of allowed packages for pip install."""

import re
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper
from src.python import ALLOWED_PACKAGES


def pip_install_whitelist_rule(input_data: ToolUseEvent):
    """Enforce whitelist of allowed packages for pip install."""
    if not input_data.tool_is_bash:
        return

    # Skip if this is a requirements.txt install (handled by other rule)
    if "-r requirements.txt" in input_data.command:
        return

    if not re.match(r'pip(\d+(\.\d+)?)?\s+install\s+', input_data.command):
        return

    # Extract package names, ignoring version specs and extras
    packages = re.findall(r'(?:^|\s)([a-zA-Z0-9][\w\-]*(?:\[[^\]]+\])?)', input_data.command[12:])

    for pkg in packages:
        if pkg not in ALLOWED_PACKAGES:
            yield PolicyHelper.deny(
                f"By policy, the package '{pkg}' is not allowed to be installed.\n"
                f"Allowed packages are: {', '.join(sorted(ALLOWED_PACKAGES))}\n"
                "If the allowed list is insufficient, please refer back to the user for approval."
            )

    yield PolicyHelper.allow()
