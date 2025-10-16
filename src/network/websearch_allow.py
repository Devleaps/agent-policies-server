"""Always allows WebSearch (search results are safe)."""

from typing import Optional
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def websearch_allow_rule(input_data: ToolUseEvent):
    if input_data.tool_name != "WebSearch":
        return

    yield PolicyHelper.allow("WebSearch always allowed")