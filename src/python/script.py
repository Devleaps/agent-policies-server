"""
Python script execution policy rule.

This rule prevents large inline Python scripts and encourages proper file-based execution.
"""

import re
from typing import Optional
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def python_script_rule(input_data: ToolUseEvent):
    """Denies large python -c commands."""
    if not input_data.tool_is_bash:
        return

    if re.match(r'python3?\s+-c\s+".{50,}"', input_data.command) or re.match(r"python3?\s+-c\s+'.{50,}'", input_data.command):
        yield PolicyHelper.deny(
            "By policy, large python -c commands have been disallowed.\n"
            "For scripts, place them in a directory and run with python.\n"
            "To test new functionality: add test cases and run with `pytest`.\n"
            "Quick verification scripts are discouraged - use the existing test framework instead."
        )

    return None