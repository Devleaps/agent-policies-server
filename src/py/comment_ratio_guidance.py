"""Provides guidance when comment-to-code ratio becomes absurdly high."""

from devleaps.policies.server.common.models import PostFileEditEvent
from src.utils import PolicyHelper


def comment_ratio_guidance_rule(input_data: PostFileEditEvent):
    """
    Analyze comment-to-code ratio and provide guidance when comments exceed code.

    Calculates the ratio of comment lines to code lines (excluding empty lines).
    Provides guidance when ratio exceeds 40%.
    """
    if not input_data.file_path.endswith('.py') or not input_data.structured_patch:
        return

    comment_count = 0
    code_count = 0

    for patch in input_data.structured_patch:
        for patch_line in patch.lines:
            stripped = patch_line.content.strip()

            if not stripped:
                continue

            if stripped.startswith('#') and not stripped.startswith('#!'):
                comment_count += 1
            else:
                code_count += 1

    if code_count > 0:
        ratio = comment_count / (code_count + comment_count)
        if ratio > 0.4:
            percentage = round(ratio * 100)
            yield PolicyHelper.guidance(
                f"Comment-to-code ratio is {percentage}%. "
                "Write self-explanatory code. Consider removing redundant comments."
            )
