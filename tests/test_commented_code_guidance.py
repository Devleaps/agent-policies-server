"""Tests for commented-out code detection."""

import pytest
from devleaps.policies.server.common.models import PostFileEditEvent, StructuredPatch, PatchLine
from src.python.commented_code_guidance import commented_code_guidance_rule


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


def test_single_indented_comment_allowed(create_post_file_edit_event):
    """Single indented comment should not trigger guidance."""
    event = create_post_file_edit_event("test.py", [
        ("added", "def foo():"),
        ("added", "    # This is a comment"),
        ("added", "    return True"),
    ])

    results = list(commented_code_guidance_rule(event))
    assert len(results) == 0


def test_consecutive_top_level_comments_allowed(create_post_file_edit_event):
    """Consecutive comments without indentation should be allowed."""
    event = create_post_file_edit_event("test.py", [
        ("added", "# This is documentation"),
        ("added", "# More documentation"),
        ("added", "# Even more documentation"),
    ])

    results = list(commented_code_guidance_rule(event))
    assert len(results) == 0


def test_two_consecutive_indented_comments_triggers(create_post_file_edit_event):
    """Two consecutive indented comments should trigger guidance."""
    event = create_post_file_edit_event("test.py", [
        ("added", "def foo():"),
        ("added", "    # def some_fn(a, b):"),
        ("added", "    #   c = a + b"),
        ("added", "    return True"),
    ])

    results = list(commented_code_guidance_rule(event))
    assert len(results) == 1
    assert "commented out" in results[0].content


def test_commented_out_function_triggers(create_post_file_edit_event):
    """Realistic commented-out function should trigger guidance."""
    event = create_post_file_edit_event("test.py", [
        ("added", "# def some_fn(a, b):"),
        ("added", "#   c = a + b"),
        ("added", "#   return c"),
        ("added", ""),
        ("added", "def active_function():"),
        ("added", "    pass"),
    ])

    results = list(commented_code_guidance_rule(event))
    assert len(results) == 1
    assert "removed" in results[0].content
