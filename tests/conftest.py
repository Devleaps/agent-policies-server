"""Shared pytest fixtures for all policy tests."""

import pytest
from src.server.models import (
    ToolUseEvent,
    PostFileEditEvent,
    StructuredPatch,
    PatchLine,
)
from src.server.enums import SourceClient
from src.main import setup_all_policies


@pytest.fixture(autouse=True, scope="session")
def register_policies():
    """Register all policy handlers once for all tests."""
    setup_all_policies()


@pytest.fixture
def bash_event():
    """Factory fixture to create ToolUseEvent for bash commands.

    Usage:
        event = bash_event("touch some-file")
        event = bash_event("rm -rf /", tool_is_bash=False)
        event = bash_event("pip install pkg", bundles=["universal", "python_pip"])
    """

    def _create(command: str, tool_is_bash: bool = True, bundles=None) -> ToolUseEvent:
        if bundles is None:
            bundles = ["universal"]
        return ToolUseEvent(
            session_id="test-session",
            source_client=SourceClient.CLAUDE_CODE,
            tool_name="Bash" if tool_is_bash else "Read",
            tool_is_bash=tool_is_bash,
            command=command,
            parameters={"command": command},
            enabled_bundles=bundles,
        )

    return _create


@pytest.fixture
def file_edit_event():
    """Factory fixture to create PostFileEditEvent for file edit guidance.

    Usage:
        # Simple additions (all lines marked "added")
        event = file_edit_event("test.py", ["# comment", "code = 1"])

        # Detailed patch with operations
        event = file_edit_event("test.py", [
            ("added", "# comment"),
            ("removed", "old code"),
            ("unchanged", "kept line")
        ])

        # With specific bundles
        event = file_edit_event("pyproject.toml", lines, bundles=["universal", "python_uv"])
    """

    def _create(
        file_path: str, lines, operation: str = "write", bundles=None
    ) -> PostFileEditEvent:
        if bundles is None:
            bundles = ["universal"]
        # Support two input formats:
        # 1. List of strings (all "added")
        # 2. List of tuples (operation, content)

        if lines and isinstance(lines[0], str):
            # Format 1: simple string list
            patch_lines = [PatchLine(operation="added", content=line) for line in lines]
        else:
            # Format 2: tuple list with operations
            patch_lines = [
                PatchLine(operation=op, content=content) for op, content in lines
            ]

        patch = StructuredPatch(
            oldStart=1,
            oldLines=0,
            newStart=1,
            newLines=len(patch_lines),
            lines=patch_lines,
        )

        return PostFileEditEvent(
            session_id="test-session",
            source_client=SourceClient.CLAUDE_CODE,
            file_path=file_path,
            operation=operation,
            structured_patch=[patch] if lines else None,
            enabled_bundles=bundles,
        )

    return _create
