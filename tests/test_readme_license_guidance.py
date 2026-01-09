"""Tests for README.md License section guidance."""

import pytest
from devleaps.policies.server.common.models import PostFileEditEvent, StructuredPatch, PatchLine
from src.universal.readme_license_guidance import readme_license_guidance_rule


@pytest.fixture
def create_post_file_edit_event():
    """Factory fixture to create PostFileEditEvent."""
    def _create(file_path: str, additions: list[str]) -> PostFileEditEvent:
        patch_lines = [PatchLine(operation="added", content=line) for line in additions]
        patch = StructuredPatch(
            oldStart=1,
            oldLines=0,
            newStart=1,
            newLines=len(patch_lines),
            lines=patch_lines
        )
        return PostFileEditEvent(
            session_id="test-session",
            source_client="claude_code",
            file_path=file_path,
            operation="write",
            structured_patch=[patch]
        )
    return _create


def test_readme_license_addition_provides_guidance(create_post_file_edit_event):
    """Adding License section to README.md should provide guidance."""
    event = create_post_file_edit_event(
        "README.md",
        additions=["## License", "", "MIT License"]
    )
    results = list(readme_license_guidance_rule(event))
    assert len(results) == 1
    assert "explicit permission" in results[0].content.lower()


def test_readme_lowercase_license_provides_guidance(create_post_file_edit_event):
    """Adding license section (lowercase) to README.md should provide guidance."""
    event = create_post_file_edit_event(
        "README.md",
        additions=["## license", "", "This project is licensed under MIT"]
    )
    results = list(readme_license_guidance_rule(event))
    assert len(results) == 1
    assert "explicit permission" in results[0].content.lower()


def test_non_readme_file_no_guidance(create_post_file_edit_event):
    """License in non-README files should match no policies."""
    event = create_post_file_edit_event(
        "src/main.py",
        additions=["# License: MIT"]
    )
    results = list(readme_license_guidance_rule(event))
    assert len(results) == 0


def test_readme_without_license_no_guidance(create_post_file_edit_event):
    """README.md edits without License keyword should match no policies."""
    event = create_post_file_edit_event(
        "README.md",
        additions=["## Installation", "", "Run `pip install package`"]
    )
    results = list(readme_license_guidance_rule(event))
    assert len(results) == 0
