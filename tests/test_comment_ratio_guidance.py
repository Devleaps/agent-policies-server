"""Tests for comment_ratio_guidance_rule."""

import pytest
from devleaps.policies.server.common.models import PostFileEditEvent, StructuredPatch, PatchLine


@pytest.fixture
def create_post_file_edit_event():
    """Factory fixture to create PostFileEditEvent with patches."""
    def _create(file_path: str, patch_lines: list) -> PostFileEditEvent:
        """Create PostFileEditEvent with given patch lines."""
        parsed_lines = [
            PatchLine(operation=op, content=content)
            for op, content in patch_lines
        ]
        patch = StructuredPatch(
            oldStart=1,
            oldLines=0,
            newStart=1,
            newLines=len(parsed_lines),
            lines=parsed_lines
        )
        return PostFileEditEvent(
            session_id="test-session",
            source_client="claude_code",
            file_path=file_path,
            operation="write",
            structured_patch=[patch]
        )
    return _create


def test_non_python_file_skipped(create_post_file_edit_event):
    """Policy should skip non-Python files."""
    from src.python.comment_ratio_guidance import comment_ratio_guidance_rule

    event = create_post_file_edit_event("test.txt", [
        ("added", "# Comment"),
        ("added", "code = 1"),
    ])

    results = list(comment_ratio_guidance_rule(event))
    assert len(results) == 0


def test_no_patches_skipped(create_post_file_edit_event):
    """Policy should skip if no patches."""
    from src.python.comment_ratio_guidance import comment_ratio_guidance_rule

    event = PostFileEditEvent(
        session_id="test-session",
        source_client="claude_code",
        file_path="test.py",
        operation="write",
        structured_patch=None
    )

    results = list(comment_ratio_guidance_rule(event))
    assert len(results) == 0


def test_low_comment_ratio_no_guidance(create_post_file_edit_event):
    """Policy should not yield guidance for low comment ratio (<40%)."""
    from src.python.comment_ratio_guidance import comment_ratio_guidance_rule

    event = create_post_file_edit_event("test.py", [
        ("added", "# Comment"),
        ("added", "code1 = 1"),
        ("added", "code2 = 2"),
        ("added", "code3 = 3"),
    ])

    results = list(comment_ratio_guidance_rule(event))
    assert len(results) == 0


def test_high_comment_ratio_yields_guidance(create_post_file_edit_event):
    """Policy should yield guidance when comment ratio > 40%."""
    from src.python.comment_ratio_guidance import comment_ratio_guidance_rule

    event = create_post_file_edit_event("test.py", [
        ("added", "# Comment 1"),
        ("added", "# Comment 2"),
        ("added", "# Comment 3"),
        ("added", "code = 1"),
    ])

    results = list(comment_ratio_guidance_rule(event))
    assert len(results) == 1
    assert "Comment-to-code ratio is 75%" in results[0].content
    assert "Write self-explanatory code" in results[0].content


def test_shebang_not_counted_as_comment(create_post_file_edit_event):
    """Shebang lines are counted as code, not as comments."""
    from src.python.comment_ratio_guidance import comment_ratio_guidance_rule

    event = create_post_file_edit_event("test.py", [
        ("added", "#!/usr/bin/env python"),
        ("added", "# Comment"),
        ("added", "code = 1"),
    ])

    results = list(comment_ratio_guidance_rule(event))
    # 1 comment / 2 code (shebang is code) = 33%, should not trigger
    assert len(results) == 0


def test_empty_lines_ignored(create_post_file_edit_event):
    """Empty lines should be ignored in ratio calculation."""
    from src.python.comment_ratio_guidance import comment_ratio_guidance_rule

    event = create_post_file_edit_event("test.py", [
        ("added", "# Comment"),
        ("added", ""),
        ("added", "code = 1"),
        ("added", ""),
        ("added", "more_code = 2"),
    ])

    results = list(comment_ratio_guidance_rule(event))
    # 1 comment / 2 code = 33%, should not trigger
    assert len(results) == 0


def test_whitespace_only_lines_ignored(create_post_file_edit_event):
    """Lines with only whitespace should be ignored."""
    from src.python.comment_ratio_guidance import comment_ratio_guidance_rule

    event = create_post_file_edit_event("test.py", [
        ("added", "# Comment"),
        ("added", "   "),
        ("added", "code = 1"),
    ])

    results = list(comment_ratio_guidance_rule(event))
    # 1 comment / 1 code = 50%, should trigger guidance
    assert len(results) == 1


def test_ratio_exactly_40_percent_no_guidance(create_post_file_edit_event):
    """Policy should not trigger at exactly 40% (threshold is >40%)."""
    from src.python.comment_ratio_guidance import comment_ratio_guidance_rule

    event = create_post_file_edit_event("test.py", [
        ("added", "# Comment"),
        ("added", "code1 = 1"),
        ("added", "code2 = 2"),
        ("added", "code3 = 3"),
    ])

    results = list(comment_ratio_guidance_rule(event))
    # 1 comment / 4 code = 20%, should not trigger
    assert len(results) == 0


def test_ratio_41_percent_yields_guidance(create_post_file_edit_event):
    """Policy should trigger for ratio just above 40%."""
    from src.python.comment_ratio_guidance import comment_ratio_guidance_rule

    # 7 comments / 10 code = 41.18%
    event = create_post_file_edit_event("test.py", [
        ("added", "# Comment 1"),
        ("added", "# Comment 2"),
        ("added", "# Comment 3"),
        ("added", "# Comment 4"),
        ("added", "# Comment 5"),
        ("added", "# Comment 6"),
        ("added", "# Comment 7"),
        ("added", "code1 = 1"),
        ("added", "code2 = 2"),
        ("added", "code3 = 3"),
        ("added", "code4 = 4"),
        ("added", "code5 = 5"),
        ("added", "code6 = 6"),
        ("added", "code7 = 7"),
        ("added", "code8 = 8"),
        ("added", "code9 = 9"),
        ("added", "code10 = 10"),
    ])

    results = list(comment_ratio_guidance_rule(event))
    assert len(results) == 1
    assert "41%" in results[0].content
