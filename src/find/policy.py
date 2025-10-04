"""Blocks find -exec for security; allows find with safe paths only."""

import re
from typing import Optional
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper, path_appears_safe


def find_exec_rule(input_data: ToolUseEvent):
    if not input_data.tool_is_bash:
        return

    if re.search(r'\bfind\b.*-exec', input_data.command):
        yield PolicyHelper.deny(
            "find commands with -exec are not allowed for security reasons"
        )


def find_safe_operations_rule(input_data: ToolUseEvent):
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    if not re.match(r'^find\s+', command):
        return

    if re.search(r'-exec', command):
        return

    is_safe, reason = path_appears_safe(command)
    if not is_safe:
        yield PolicyHelper.deny(
            f"By policy, find with {reason}.\n"
            "Use relative paths only (e.g., `find . -name \"*.txt\"` or `find subdir -type f`).\n"
            "If you need to search upward, first `cd` to the target directory."
        )

    yield PolicyHelper.allow()


all_rules = [find_exec_rule, find_safe_operations_rule]
