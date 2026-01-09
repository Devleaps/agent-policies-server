"""Test for DEPRECATED keyword in legacy code guidance."""

import pytest
from devleaps.policies.server.common.models import PostFileEditEvent, StructuredPatch, PatchLine
from src.universal.legacy_code_guidance import legacy_code_guidance_rule


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


def test_deprecated_keyword_triggers_guidance(create_post_file_edit_event):
    """DEPRECATED keyword should trigger legacy code guidance."""
    event = create_post_file_edit_event("test.py", [
        ("added", "# DEPRECATED: This function will be removed"),
        ("added", "def old_function():"),
        ("added", "    pass"),
    ])

    results = list(legacy_code_guidance_rule(event))
    assert len(results) == 1
    assert "legacy" in results[0].content.lower() or "deprecated" in results[0].content.lower()


def test_deprecated_lowercase_triggers_guidance(create_post_file_edit_event):
    """deprecated in lowercase should also trigger guidance."""
    event = create_post_file_edit_event("test.py", [
        ("added", "# This method is deprecated"),
        ("added", "def old_method():"),
        ("added", "    pass"),
    ])

    results = list(legacy_code_guidance_rule(event))
    assert len(results) == 1
