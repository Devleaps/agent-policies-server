"""Provides guidance when License section is added to README.md."""

import re
from devleaps.policies.server.common.models import PostFileEditEvent
from src.utils import PolicyHelper


def readme_license_guidance_rule(input_data: PostFileEditEvent):
    """Provide guidance when AI adds License section to README.md."""
    if not input_data.structured_patch:
        return

    file_path = input_data.file_path.lower()

    # Only check README.md files
    if not file_path.endswith("readme.md"):
        return

    # Check if any added lines contain "license"
    for patch in input_data.structured_patch:
        for patch_line in patch.lines:
            if patch_line.operation == "added":
                if re.search(r'\blicense\b', patch_line.content, re.IGNORECASE):
                    yield PolicyHelper.guidance(
                        "An AI is only allowed to add a License segment to documentation when explicit "
                        "permission was granted by the user, and the user selected the license documented."
                    )
                    return
