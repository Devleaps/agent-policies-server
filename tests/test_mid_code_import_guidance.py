"""Tests for mid_code_import_guidance_rule."""

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
    from src.python.mid_code_import_guidance import mid_code_import_guidance_rule

    event = create_post_file_edit_event("test.txt", [
        ("added", "def function():"),
        ("added", "    import os"),
    ])

    results = list(mid_code_import_guidance_rule(event))
    assert len(results) == 0


def test_no_patches_skipped(create_post_file_edit_event):
    """Policy should skip if no patches."""
    from src.python.mid_code_import_guidance import mid_code_import_guidance_rule

    event = PostFileEditEvent(
        session_id="test-session",
        source_client="claude_code",
        file_path="test.py",
        operation="write",
        structured_patch=None
    )

    results = list(mid_code_import_guidance_rule(event))
    assert len(results) == 0


def test_top_level_import_allowed(create_post_file_edit_event):
    """Top-level imports with no leading whitespace should be allowed."""
    from src.python.mid_code_import_guidance import mid_code_import_guidance_rule

    event = create_post_file_edit_event("test.py", [
        ("added", "import os"),
        ("added", "import sys"),
        ("added", "from typing import List"),
    ])

    results = list(mid_code_import_guidance_rule(event))
    assert len(results) == 0


def test_import_in_comment_allowed(create_post_file_edit_event):
    """Imports in comments should be allowed."""
    from src.python.mid_code_import_guidance import mid_code_import_guidance_rule

    event = create_post_file_edit_event("test.py", [
        ("added", "# import x"),
        ("added", "# from x import y"),
        ("added", "def function():"),
        ("added", "    # import z"),
        ("added", "    pass"),
    ])

    results = list(mid_code_import_guidance_rule(event))
    assert len(results) == 0


def test_indented_import_triggers_guidance(create_post_file_edit_event):
    """Indented import statements should trigger guidance."""
    from src.python.mid_code_import_guidance import mid_code_import_guidance_rule

    event = create_post_file_edit_event("test.py", [
        ("added", "def function():"),
        ("added", "    import os"),
    ])

    results = list(mid_code_import_guidance_rule(event))
    assert len(results) == 1
    assert "top of the file" in results[0].content


def test_indented_from_import_triggers_guidance(create_post_file_edit_event):
    """Indented from...import statements should trigger guidance."""
    from src.python.mid_code_import_guidance import mid_code_import_guidance_rule

    event = create_post_file_edit_event("test.py", [
        ("added", "def function():"),
        ("added", "    from os import path"),
    ])

    results = list(mid_code_import_guidance_rule(event))
    assert len(results) == 1
    assert "top of the file" in results[0].content


def test_class_level_import_triggers_guidance(create_post_file_edit_event):
    """Imports inside classes should trigger guidance."""
    from src.python.mid_code_import_guidance import mid_code_import_guidance_rule

    event = create_post_file_edit_event("test.py", [
        ("added", "class MyClass:"),
        ("added", "    import json"),
    ])

    results = list(mid_code_import_guidance_rule(event))
    assert len(results) == 1


def test_nested_import_triggers_guidance(create_post_file_edit_event):
    """Deeply nested imports should trigger guidance."""
    from src.python.mid_code_import_guidance import mid_code_import_guidance_rule

    event = create_post_file_edit_event("test.py", [
        ("added", "def outer():"),
        ("added", "    def inner():"),
        ("added", "        import sys"),
    ])

    results = list(mid_code_import_guidance_rule(event))
    assert len(results) == 1


def test_tab_indented_import_triggers_guidance(create_post_file_edit_event):
    """Tab-indented imports should trigger guidance."""
    from src.python.mid_code_import_guidance import mid_code_import_guidance_rule

    event = create_post_file_edit_event("test.py", [
        ("added", "def function():"),
        ("added", "\timport os"),
    ])

    results = list(mid_code_import_guidance_rule(event))
    assert len(results) == 1


def test_empty_lines_and_comments_skipped(create_post_file_edit_event):
    """Empty lines and comments should be skipped."""
    from src.python.mid_code_import_guidance import mid_code_import_guidance_rule

    event = create_post_file_edit_event("test.py", [
        ("added", ""),
        ("added", "# This is a comment"),
        ("added", "import os"),
    ])

    results = list(mid_code_import_guidance_rule(event))
    assert len(results) == 0


def test_stops_after_first_violation(create_post_file_edit_event):
    """Policy should return after finding first violation."""
    from src.python.mid_code_import_guidance import mid_code_import_guidance_rule

    event = create_post_file_edit_event("test.py", [
        ("added", "def function1():"),
        ("added", "    import os"),
        ("added", ""),
        ("added", "def function2():"),
        ("added", "    import sys"),
    ])

    results = list(mid_code_import_guidance_rule(event))
    # Should find the first violation and return
    assert len(results) == 1


def test_mixed_valid_and_invalid(create_post_file_edit_event):
    """Top-level imports followed by indented import should trigger guidance."""
    from src.python.mid_code_import_guidance import mid_code_import_guidance_rule

    event = create_post_file_edit_event("test.py", [
        ("added", "import os"),
        ("added", "from typing import List"),
        ("added", ""),
        ("added", "def function():"),
        ("added", "    import json"),
    ])

    results = list(mid_code_import_guidance_rule(event))
    assert len(results) == 1


def test_import_as_triggers_guidance_when_indented(create_post_file_edit_event):
    """Indented 'import x as y' should trigger guidance."""
    from src.python.mid_code_import_guidance import mid_code_import_guidance_rule

    event = create_post_file_edit_event("test.py", [
        ("added", "def function():"),
        ("added", "    import numpy as np"),
    ])

    results = list(mid_code_import_guidance_rule(event))
    assert len(results) == 1


def test_from_import_with_multiple_items(create_post_file_edit_event):
    """Indented 'from x import a, b, c' should trigger guidance."""
    from src.python.mid_code_import_guidance import mid_code_import_guidance_rule

    event = create_post_file_edit_event("test.py", [
        ("added", "def function():"),
        ("added", "    from os.path import join, exists, dirname"),
    ])

    results = list(mid_code_import_guidance_rule(event))
    assert len(results) == 1


def test_realistic_code_structure(create_post_file_edit_event):
    """Test with realistic Python code structure."""
    from src.python.mid_code_import_guidance import mid_code_import_guidance_rule

    event = create_post_file_edit_event("test.py", [
        ("added", "import os"),
        ("added", "from typing import Optional"),
        ("added", ""),
        ("added", ""),
        ("added", "class MyClass:"),
        ("added", '    """A sample class."""'),
        ("added", ""),
        ("added", "    def process(self):"),
        ("added", "        # Lazy import for performance"),
        ("added", "        import expensive_module"),
        ("added", "        return expensive_module.process()"),
    ])

    results = list(mid_code_import_guidance_rule(event))
    assert len(results) == 1
    assert "lazy importing" in results[0].content
