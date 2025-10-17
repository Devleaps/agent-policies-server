"""Provides guidance when comments redundantly describe what code already says."""

import re
from devleaps.policies.server.common.models import PostFileEditEvent
from src.utils import PolicyHelper


def _extract_keywords(text: str) -> set:
    """Extract keywords from text, splitting on underscores and non-word chars."""
    # Split on underscores and extract words, filtering by length > 2
    words = re.findall(r'[a-z]+', text.lower())
    return {w for w in words if len(w) > 2}


def comment_overlap_guidance_rule(input_data: PostFileEditEvent):
    """
    Detect when comments redundantly describe what code already says.

    Analyzes what percentage of comment words appear in the adjacent code line.
    Checks both standalone comments and inline comments (code # comment).
    Provides guidance when >= 40% of comment words appear in the code.
    """
    if not input_data.file_path.endswith('.py') or not input_data.structured_patch:
        return

    for patch in input_data.structured_patch:
        for i, patch_line in enumerate(patch.lines):
            stripped = patch_line.content.strip()

            # Check for inline comments (code # comment)
            if '#' in stripped and not stripped.startswith('#'):
                parts = stripped.split('#', 1)
                code_part = parts[0].strip()
                comment_part = parts[1].strip()

                # Skip if comment is shebang or empty
                if not comment_part or comment_part.startswith('!'):
                    continue

                comment_keywords = _extract_keywords(comment_part)
                code_keywords = _extract_keywords(code_part)

                if comment_keywords and code_keywords:
                    overlap = comment_keywords & code_keywords
                    overlap_ratio = len(overlap) / len(comment_keywords)

                    if overlap_ratio >= 0.4:
                        yield PolicyHelper.guidance(
                            "Ensure comments add value beyond describing what's obvious from the code. "
                            "This comment may be redundant with the code it describes."
                        )
                        return

            # Check for standalone comments
            if not stripped.startswith('#') or stripped.startswith('#!'):
                continue

            comment_keywords = _extract_keywords(stripped[1:])

            if i + 1 < len(patch.lines):
                next_line = patch.lines[i + 1].content.strip()

                if next_line and not next_line.startswith('#'):
                    code_keywords = _extract_keywords(next_line)

                    if comment_keywords and code_keywords:
                        # Calculate % of comment words that appear in code
                        overlap = comment_keywords & code_keywords
                        overlap_ratio = len(overlap) / len(comment_keywords)

                        if overlap_ratio >= 0.4:
                            yield PolicyHelper.guidance(
                                "Ensure comments add value beyond describing what's obvious from the code. "
                                "This comment may be redundant with the code it describes."
                            )
                            return
