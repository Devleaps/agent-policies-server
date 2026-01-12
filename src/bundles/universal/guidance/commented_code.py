"""Provides guidance when large blocks of code are commented out."""

import re
from devleaps.policies.server.common.models import PostFileEditEvent
from src.utils import PolicyHelper


def commented_code_guidance_rule(input_data: PostFileEditEvent):
    """
    Detect 2+ consecutive comments with excessive leading whitespace.

    This pattern indicates commented-out code blocks that should be removed
    in a Git project rather than maintained for historical purposes.

    Detects two patterns:
    1. Comments with leading whitespace before # (indented comments)
    2. Comments where the content after # has leading whitespace (commented-out indented code)
    """
    if not input_data.file_path.endswith('.py') or not input_data.structured_patch:
        return

    # Pattern to match comments with leading whitespace before #
    indented_comment_pattern = re.compile(r'^\s+#')

    # Pattern to match comments with whitespace after # (commented-out indented code)
    commented_indented_code_pattern = re.compile(r'^#\s{2,}')

    for patch in input_data.structured_patch:
        consecutive_commented_code = 0

        for patch_line in patch.lines:
            line_content = patch_line.content
            stripped = line_content.strip()

            # Check if this is a comment line with indentation pattern
            is_commented_code = (
                indented_comment_pattern.match(line_content) or
                commented_indented_code_pattern.match(line_content)
            )

            if is_commented_code:
                consecutive_commented_code += 1

                # If we have 2+ consecutive commented code lines, trigger guidance
                if consecutive_commented_code >= 2:
                    yield PolicyHelper.guidance(
                        "If a large segment of code was commented out within a Git project, "
                        "it should be removed rather than maintained for historical purposes."
                    )
                    return
            else:
                # Reset counter on lines that don't match the pattern
                consecutive_commented_code = 0
