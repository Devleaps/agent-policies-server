"""Python import placement guidance."""

import re
from src.server.common.models import PostFileEditEvent
from src.utils import PolicyHelper


def mid_code_import_guidance_rule(input_data: PostFileEditEvent):
    """
    Detect when import statements appear indented (mid-code).

    Import statements should be at the top of the file with no leading whitespace.
    Imports preceded by whitespace indicate they're inside functions, classes, or
    other blocks, which is discouraged.

    Allowed:
    - import x
    - from x import y
    - # import x (in comments)

    Not allowed:
    - def function():
          import x
    - class Foo:
        from x import y
    """
    import_pattern = re.compile(r'^\s+(import\s+\S+|from\s+\S+\s+import\s+)')

    for patch in input_data.structured_patch:
        for patch_line in patch.lines:
            line_content = patch_line.content
            stripped = line_content.strip()

            if not stripped or stripped.startswith('#'):
                continue

            if import_pattern.match(line_content):
                yield PolicyHelper.guidance(
                    "Import statements should be at the top of the file, not nested inside "
                    "functions, classes, or other blocks. Move imports to the module level "
                    "unless there's a specific reason for lazy importing (e.g., avoiding "
                    "circular dependencies or expensive imports)."
                )
                return
