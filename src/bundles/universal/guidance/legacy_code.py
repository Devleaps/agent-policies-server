"""Guidance for legacy code modifications."""

import re
from src.server.common.models import PostFileEditEvent
from src.utils import PolicyHelper


def legacy_code_guidance_rule(input_data: PostFileEditEvent):
    """Provide guidance when modifying code that mentions legacy or backwards compatibility.

    Detects keywords suggesting backwards compatibility concerns and prompts
    for confirmation that these changes are intentional.
    """
    if not input_data.structured_patch:
        return

    legacy_patterns = [
        r'\blegacy\b',
        r'\bbackwards\s+compatibility\b',
        r'\bbackward\s+compatibility\b',
        r'\bdeprecated\b'
    ]

    for patch in input_data.structured_patch:
        for patch_line in patch.lines:
            line = patch_line.content.lower()
            for pattern in legacy_patterns:
                if re.search(pattern, line):
                    yield PolicyHelper.guidance(
                        "Detected a note on backwards compatibility, legacy, or deprecated code. "
                        "Are you sure about backwards compatibility as a requirement? If not explicitly requested, check with the user first."
                    )
                    return
