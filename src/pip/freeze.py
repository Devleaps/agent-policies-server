"""Allows pip freeze to requirements.txt and blocks manual requirements.txt editing."""

import re
from typing import Optional
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def pip_freeze_rule(input_data: ToolUseEvent):
    if not input_data.tool_is_bash:
        return

    if re.match(r'pip3?\s+freeze\s*>\s*requirements\.txt', input_data.command):
        yield PolicyHelper.allow()

    return


def requirements_rule(input_data: ToolUseEvent):
    if input_data.tool_name == "Write" or input_data.tool_name == "Edit":
        parameters = input_data.parameters
        if isinstance(parameters, dict):
            file_path = parameters.get("file_path", "")
            if file_path.endswith("requirements.txt"):
                yield PolicyHelper.deny(
                    "By policy, manual editing of requirements.txt has been disallowed.\n"
                    "To capture the current dependencies, use `pip freeze > requirements.txt` instead.\n"
                    "To add dependencies, use `pip install <package>`. Install the latest version when free to do so.\n"
                    "To remove dependencies, use `pip uninstall <package>`."
                )

    return None