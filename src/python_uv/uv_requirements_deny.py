"""Deny requirements.txt creation and modification."""

from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def uv_requirements_txt_deny_rule(input_data: ToolUseEvent):
    """Block creation or modification of requirements.txt - use pyproject.toml instead."""
    if input_data.tool_name in ("Write", "Edit"):
        parameters = input_data.parameters
        if isinstance(parameters, dict):
            file_path = parameters.get("file_path", "")
            if file_path.endswith("requirements.txt"):
                yield PolicyHelper.deny(
                    "Don't use requirements.txt. Use pyproject.toml instead.\n"
                    "Use 'uv add package-name' to add dependencies to pyproject.toml."
                )
