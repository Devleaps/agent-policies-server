"""Test that all guidance messages properly use backtick quotes for commands."""

import re
import os
from pathlib import Path


def test_all_guidance_messages_use_backticks():
    """Verify that all PolicyHelper.deny/guidance messages use backticks for commands."""

    # Common command names that should be backtick-quoted
    command_patterns = [
        r"(?<![`'])(\bpip\b)(?![`'])",
        r"(?<![`'])(\buv run\b)(?![`'])",
        r"(?<![`'])(\buv sync\b)(?![`'])",
        r"(?<![`'])(\bpytest\b)(?![`'])",
        r"(?<![`'])(\btrash\b)(?![`'])",
        r"(?<![`'])(\bgit\s+\w+\b)(?![`'])",
    ]

    src_path = Path(__file__).parent.parent / "src"
    violations = []

    for py_file in src_path.rglob("*.py"):
        content = py_file.read_text()

        # Find all PolicyHelper.deny() and PolicyHelper.guidance() calls
        for match in re.finditer(r'PolicyHelper\.(deny|guidance)\s*\(\s*["\'](.+?)["\']', content, re.DOTALL):
            message = match.group(2)

            # Check if message contains unquoted commands
            for pattern in command_patterns:
                if re.search(pattern, message):
                    violations.append(f"{py_file.relative_to(src_path.parent)}: {message[:100]}")

    if violations:
        print("\nFound unquoted commands in guidance messages:")
        for v in violations:
            print(f"  - {v}")

    assert len(violations) == 0, f"Found {len(violations)} messages with unquoted commands"
