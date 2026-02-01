"""Python code comment quality guidance."""

import re
from src.server.models import PostFileEditEvent, PolicyGuidance


def comment_ratio_guidance_rule(input_data: PostFileEditEvent):
    """
    Analyze comment-to-code ratio and provide guidance when comments exceed code.

    Calculates the ratio of comment lines to code lines (excluding empty lines).
    Provides guidance when ratio exceeds 40%.
    """
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
            yield PolicyGuidance(content=
                f"Comment-to-code ratio is {percentage}%. "
                "Write self-explanatory code. Consider removing redundant comments."
            )


def _extract_keywords(text: str) -> set:
    """Extract keywords from text, splitting on underscores and non-word chars."""
    words = re.findall(r'[a-z]+', text.lower())
    return {w for w in words if len(w) > 2}


def comment_overlap_guidance_rule(input_data: PostFileEditEvent):
    """
    Detect when comments redundantly describe what code already says.

    Analyzes what percentage of comment words appear in the adjacent code line.
    Checks both standalone comments and inline comments (code # comment).
    Provides guidance when >= 40% of comment words appear in the code.
    """
    for patch in input_data.structured_patch:
        for i, patch_line in enumerate(patch.lines):
            stripped = patch_line.content.strip()

            # Check for inline comments (code # comment)
            if '#' in stripped and not stripped.startswith('#'):
                parts = stripped.split('#', 1)
                code_part = parts[0].strip()
                comment_part = parts[1].strip()

                if not comment_part or comment_part.startswith('!'):
                    continue

                comment_keywords = _extract_keywords(comment_part)
                code_keywords = _extract_keywords(code_part)

                if comment_keywords and code_keywords:
                    overlap = comment_keywords & code_keywords
                    overlap_ratio = len(overlap) / len(comment_keywords)

                    if overlap_ratio >= 0.4:
                        yield PolicyGuidance(content=
                            "Ensure comments add value beyond describing what's obvious from the code. "
                            "This comment may be redundant with the code it describes. "
                            "Comments are fine when they add value beyond the code or separate segments of code."
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
                        overlap = comment_keywords & code_keywords
                        overlap_ratio = len(overlap) / len(comment_keywords)

                        if overlap_ratio >= 0.4:
                            yield PolicyGuidance(content=
                                "Ensure comments add value beyond describing what's obvious from the code. "
                                "This comment may be redundant with the code it describes. "
                                "Comments are fine when they add value beyond the code or separate segments of code."
                            )
                            return


def commented_code_guidance_rule(input_data: PostFileEditEvent):
    """
    Detect 2+ consecutive comments with excessive leading whitespace.

    This pattern indicates commented-out code blocks that should be removed
    in a Git project rather than maintained for historical purposes.

    Detects two patterns:
    1. Comments with leading whitespace before # (indented comments)
    2. Comments where the content after # has leading whitespace (commented-out indented code)
    """
    indented_comment_pattern = re.compile(r'^\s+#')
    commented_indented_code_pattern = re.compile(r'^#\s{2,}')

    for patch in input_data.structured_patch:
        consecutive_commented_code = 0

        for patch_line in patch.lines:
            line_content = patch_line.content
            stripped = line_content.strip()

            is_commented_code = (
                indented_comment_pattern.match(line_content) or
                commented_indented_code_pattern.match(line_content)
            )

            if is_commented_code:
                consecutive_commented_code += 1

                if consecutive_commented_code >= 2:
                    yield PolicyGuidance(content=
                        "If a large segment of code was commented out within a Git project, "
                        "it should be removed rather than maintained for historical purposes."
                    )
                    return
            else:
                consecutive_commented_code = 0


def legacy_code_guidance_rule(input_data: PostFileEditEvent):
    """Provide guidance when modifying code that mentions legacy or backwards compatibility.

    Detects keywords suggesting backwards compatibility concerns and prompts
    for confirmation that these changes are intentional.
    """
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
                    yield PolicyGuidance(content=
                        "Detected a note on backwards compatibility, legacy, or deprecated code. "
                        "Are you sure about backwards compatibility as a requirement? If not explicitly requested, check with the user first."
                    )
                    return
