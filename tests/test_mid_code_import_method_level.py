"""Test for method-level import detection."""

import pytest
from devleaps.policies.server.common.models import PostFileEditEvent, StructuredPatch, PatchLine
from src.python.mid_code_import_guidance import mid_code_import_guidance_rule


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


def test_method_level_import_with_docstring(create_post_file_edit_event):
    """Method-level imports should be detected even after docstrings."""
    event = create_post_file_edit_event("test.py", [
        ("added", "def process_data(self, data: Any) -> Result:"),
        ("added", '    """Process the data."""'),
        ("added", "    import json"),
        ("added", "    return json.loads(data)"),
    ])

    results = list(mid_code_import_guidance_rule(event))
    assert len(results) == 1
    assert "top of the file" in results[0].content
