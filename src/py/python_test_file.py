"""Blocks running test files directly with python (test_*.py pattern)."""

import re
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def python_test_file_rule(input_data: ToolUseEvent):
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Match python commands running files with test patterns
    # Covers: python test_foo.py, python3 some/path/test_bar.py, etc.
    if re.match(r'python3?\s+.*test_.*\.py', command):
        yield PolicyHelper.deny(
            "By policy, running python directly on test files is disallowed.\n"
            "To test new functionality: add test cases and run with `pytest`.\n"
            "Quick verification scripts are discouraged - use the existing test framework instead."
        )
