"""
WebSearch allow policy rule.

This rule always allows WebSearch commands since search results are generally safe.
"""

from typing import Optional
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def websearch_allow_rule(input_data: ToolUseEvent):
    """Always allows WebSearch commands."""
    if input_data.tool_name != "WebSearch":
        return

    yield PolicyHelper.allow("WebSearch always allowed")