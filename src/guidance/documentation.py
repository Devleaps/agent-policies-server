"""Documentation-related guidance."""

import re
from src.server.models import PostFileEditEvent, PolicyGuidance


def license_guidance_rule(input_data: PostFileEditEvent):
    """Provide guidance when AI adds License section to documentation."""
    if not input_data.structured_patch:
        return

    for patch in input_data.structured_patch:
        for patch_line in patch.lines:
            if patch_line.operation == "added":
                if re.search(r"\blicense\b", patch_line.content, re.IGNORECASE):
                    yield PolicyGuidance(
                        content="An AI is only allowed to add a License segment to documentation when explicit "
                        "permission was granted by the user, and the user selected the license documented."
                    )
                    return
