"""Tests for comment_overlap_guidance_rule."""

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
    from src.py.comment_overlap_guidance import comment_overlap_guidance_rule

    event = create_post_file_edit_event("test.txt", [
        ("added", "# Initialize database"),
        ("added", "db = initialize_database()"),
    ])

    results = list(comment_overlap_guidance_rule(event))
    assert len(results) == 0


def test_no_patches_skipped(create_post_file_edit_event):
    """Policy should skip if no patches."""
    from src.py.comment_overlap_guidance import comment_overlap_guidance_rule

    event = PostFileEditEvent(
        session_id="test-session",
        source_client="claude_code",
        file_path="test.py",
        operation="write",
        structured_patch=None
    )

    results = list(comment_overlap_guidance_rule(event))
    assert len(results) == 0


def test_no_comments_no_guidance(create_post_file_edit_event):
    """Policy should not yield guidance if there are no comments."""
    from src.py.comment_overlap_guidance import comment_overlap_guidance_rule

    event = create_post_file_edit_event("test.py", [
        ("added", "db = initialize_database()"),
        ("added", "cache = initialize_cache()"),
    ])

    results = list(comment_overlap_guidance_rule(event))
    assert len(results) == 0


def test_comment_without_next_line_skipped(create_post_file_edit_event):
    """Policy should skip comments without adjacent code."""
    from src.py.comment_overlap_guidance import comment_overlap_guidance_rule

    event = create_post_file_edit_event("test.py", [
        ("added", "# This is a comment"),
    ])

    results = list(comment_overlap_guidance_rule(event))
    assert len(results) == 0


def test_shebang_not_analyzed(create_post_file_edit_event):
    """Shebang lines should not be analyzed as comments."""
    from src.py.comment_overlap_guidance import comment_overlap_guidance_rule

    event = create_post_file_edit_event("test.py", [
        ("added", "#!/usr/bin/env python"),
        ("added", "code = 1"),
    ])

    results = list(comment_overlap_guidance_rule(event))
    assert len(results) == 0


def test_comment_next_to_another_comment_skipped(create_post_file_edit_event):
    """Policy should skip if next line is also a comment."""
    from src.py.comment_overlap_guidance import comment_overlap_guidance_rule

    event = create_post_file_edit_event("test.py", [
        ("added", "# Comment 1"),
        ("added", "# Comment 2"),
    ])

    results = list(comment_overlap_guidance_rule(event))
    assert len(results) == 0


def test_high_overlap_yields_guidance(create_post_file_edit_event):
    """Policy should yield guidance when >= 40% of comment words appear in code."""
    from src.py.comment_overlap_guidance import comment_overlap_guidance_rule

    # Comment: "Initialize database" -> {"initialize", "database"} (2 words)
    # Code: "database = initialize_database()" -> {"database", "initialize"} (2 words)
    # Overlap: 2/2 = 100% >= 40%, should trigger
    event = create_post_file_edit_event("test.py", [
        ("added", "# Initialize database"),
        ("added", "database = initialize_database()"),
    ])

    results = list(comment_overlap_guidance_rule(event))
    assert len(results) == 1
    assert "redundant" in results[0].content.lower()


def test_low_overlap_no_guidance(create_post_file_edit_event):
    """Policy should not yield guidance when < 40% of comment words appear in code."""
    from src.py.comment_overlap_guidance import comment_overlap_guidance_rule

    event = create_post_file_edit_event("test.py", [
        ("added", "# Setup the system"),
        ("added", "db = connect_to_database()"),
    ])

    results = list(comment_overlap_guidance_rule(event))
    # Comment: {"setup", "system"} (2 words)
    # Code: {"connect", "database"} (2 words)
    # Overlap: 0/2 = 0% < 40%, should not trigger
    assert len(results) == 0


def test_significant_overlap_example(create_post_file_edit_event):
    """Test overlap detection when >= 40% of comment words are in code."""
    from src.py.comment_overlap_guidance import comment_overlap_guidance_rule

    event = create_post_file_edit_event("test.py", [
        ("added", "# Open config file"),
        ("added", "config = open_file(name)"),
    ])

    results = list(comment_overlap_guidance_rule(event))
    # Comment: {"open", "config", "file"} (3 words)
    # Code: {"config", "open", "file", "name"} (4 words)
    # Overlap: {"open", "config", "file"} = 3/3 = 100% >= 40%, should trigger
    assert len(results) == 1


def test_cache_overlap_example(create_post_file_edit_event):
    """Test comment with word overlap >= 40%."""
    from src.py.comment_overlap_guidance import comment_overlap_guidance_rule

    event = create_post_file_edit_event("test.py", [
        ("added", "# Configure cache settings"),
        ("added", "cache.configure(ttl=3600)"),
    ])

    results = list(comment_overlap_guidance_rule(event))
    # Comment: {"configure", "cache", "settings"} (3 words)
    # Code: {"cache", "configure"} (2 words)
    # Overlap: {"cache", "configure"} = 2/3 = 67% >= 40%, should trigger
    assert len(results) == 1


def test_stops_after_first_overlap(create_post_file_edit_event):
    """Policy should return after finding first overlap."""
    from src.py.comment_overlap_guidance import comment_overlap_guidance_rule

    event = create_post_file_edit_event("test.py", [
        ("added", "# Initialize database"),
        ("added", "db = initialize_database()"),
        ("added", "# Configure cache settings"),
        ("added", "cache.configure(ttl=3600)"),
    ])

    results = list(comment_overlap_guidance_rule(event))
    # Should find the first overlap and return
    assert len(results) == 1


def test_empty_line_between_comment_and_code(create_post_file_edit_event):
    """Policy should skip if there's an empty line between comment and code."""
    from src.py.comment_overlap_guidance import comment_overlap_guidance_rule

    event = create_post_file_edit_event("test.py", [
        ("added", "# Initialize database"),
        ("added", ""),
        ("added", "db = initialize_database()"),
    ])

    results = list(comment_overlap_guidance_rule(event))
    # Empty line means next line is empty, not code
    assert len(results) == 0


def test_minimal_overlap_just_under_threshold(create_post_file_edit_event):
    """Test overlap ratio just under 40% threshold."""
    from src.py.comment_overlap_guidance import comment_overlap_guidance_rule

    event = create_post_file_edit_event("test.py", [
        ("added", "# Create new file system"),
        ("added", "path = filesystem_create()"),
    ])

    results = list(comment_overlap_guidance_rule(event))
    # Comment: {"create", "new", "file", "system"} (4 words)
    # Code: {"path", "filesystem", "create"} (3 words, filesystem is one word due to no underscores)
    # Overlap: {"create"} = 1/4 = 25% < 40%, should not trigger
    assert len(results) == 0


def test_docstring_not_analyzed(create_post_file_edit_event):
    """Policy should only look at # comments, not docstrings."""
    from src.py.comment_overlap_guidance import comment_overlap_guidance_rule

    event = create_post_file_edit_event("test.py", [
        ('added', '"""Initialize database connection"""'),
        ("added", "db = initialize_database()"),
    ])

    results = list(comment_overlap_guidance_rule(event))
    # Docstrings don't start with #, so should not be analyzed
    assert len(results) == 0


def test_inline_comment_high_overlap(create_post_file_edit_event):
    """Policy should detect high overlap in inline comments."""
    from src.py.comment_overlap_guidance import comment_overlap_guidance_rule

    event = create_post_file_edit_event("test.py", [
        ("added", "path = open_file(name)  # Open file"),
    ])

    results = list(comment_overlap_guidance_rule(event))
    # Code: {"path", "open", "file", "name"}
    # Comment: {"open", "file"}
    # Overlap: 2/2 = 100% >= 40%, should trigger
    assert len(results) == 1


def test_inline_comment_low_overlap(create_post_file_edit_event):
    """Policy should not flag inline comments with low overlap."""
    from src.py.comment_overlap_guidance import comment_overlap_guidance_rule

    event = create_post_file_edit_event("test.py", [
        ("added", "path = connect_to_server()  # Use primary server"),
    ])

    results = list(comment_overlap_guidance_rule(event))
    # Code: {"path", "connect", "server"}
    # Comment: {"use", "primary", "server"}
    # Overlap: {"server"} = 1/3 = 33% < 40%, should not trigger
    assert len(results) == 0


def test_inline_comment_just_under_threshold(create_post_file_edit_event):
    """Policy should not trigger inline comments at exactly 40%."""
    from src.py.comment_overlap_guidance import comment_overlap_guidance_rule

    event = create_post_file_edit_event("test.py", [
        ("added", "db_config = initialize_database()  # Initialize the database"),
    ])

    results = list(comment_overlap_guidance_rule(event))
    # Code: {"db", "config", "initialize", "database"}
    # Comment: {"initialize", "database"}
    # Overlap: 2/2 = 100% >= 40%, should trigger
    assert len(results) == 1


def test_inline_comment_empty_comment(create_post_file_edit_event):
    """Policy should skip inline comments that are empty after #."""
    from src.py.comment_overlap_guidance import comment_overlap_guidance_rule

    event = create_post_file_edit_event("test.py", [
        ("added", "code = function()  #"),
    ])

    results = list(comment_overlap_guidance_rule(event))
    # Empty comment after #, should skip
    assert len(results) == 0
