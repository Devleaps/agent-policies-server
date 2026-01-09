"""Tests for git add with specific files policy."""

import pytest
from devleaps.policies.server.common.models import ToolUseEvent
from devleaps.policies.server.common.enums import SourceClient
from src.git.git_policy import git_add_rule


@pytest.fixture
def create_tool_use_event():
    """Factory fixture to create ToolUseEvent."""
    def _create(command: str, tool_is_bash: bool = True) -> ToolUseEvent:
        return ToolUseEvent(
            session_id="test-session",
            source_client=SourceClient.CLAUDE_CODE,
            tool_name="Bash" if tool_is_bash else "Read",
            tool_is_bash=tool_is_bash,
            command=command,
            parameters={"command": command}
        )
    return _create


def test_git_add_a_flag_allowed(create_tool_use_event):
    """Allow git add -A without guidance."""
    event = create_tool_use_event("git add -A")
    results = list(git_add_rule(event))
    # Should yield allow decision only, no guidance
    decisions = [r for r in results if hasattr(r, 'action')]
    assert len(decisions) == 1
    assert decisions[0].action == "allow"


def test_git_add_single_file_allowed(create_tool_use_event):
    """Allow git add with single file."""
    event = create_tool_use_event("git add file.txt")
    results = list(git_add_rule(event))
    decisions = [r for r in results if hasattr(r, 'action')]
    assert len(decisions) == 1
    assert decisions[0].action == "allow"


def test_git_add_path_file_allowed(create_tool_use_event):
    """Allow git add with file in subdirectory."""
    event = create_tool_use_event("git add src/file.py")
    results = list(git_add_rule(event))
    decisions = [r for r in results if hasattr(r, 'action')]
    assert len(decisions) == 1
    assert decisions[0].action == "allow"


def test_git_add_multiple_files_allowed(create_tool_use_event):
    """Allow git add with multiple files."""
    event = create_tool_use_event("git add file1.txt file2.txt")
    results = list(git_add_rule(event))
    decisions = [r for r in results if hasattr(r, 'action')]
    assert len(decisions) == 1
    assert decisions[0].action == "allow"
