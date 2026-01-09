"""Tests for git mv command policy."""

import pytest
from devleaps.policies.server.common.models import ToolUseEvent
from devleaps.policies.server.common.enums import SourceClient
from src.git.git_policy import git_mv_rule


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


def test_git_mv_simple_rename(create_tool_use_event):
    """Allow git mv with simple file rename."""
    event = create_tool_use_event("git mv oldfile.txt newfile.txt")
    results = list(git_mv_rule(event))
    assert len(results) == 1
    assert results[0].action == "allow"


def test_git_mv_with_force_flag(create_tool_use_event):
    """Allow git mv with -f flag."""
    event = create_tool_use_event("git mv -f src/old.py src/new.py")
    results = list(git_mv_rule(event))
    assert len(results) == 1
    assert results[0].action == "allow"


def test_git_mv_absolute_path_denied(create_tool_use_event):
    """Block git mv with absolute path."""
    event = create_tool_use_event("git mv /tmp/file.txt local.txt")
    results = list(git_mv_rule(event))
    assert len(results) == 1
    assert results[0].action == "deny"


def test_git_mv_parent_directory_denied(create_tool_use_event):
    """Block git mv with parent directory traversal."""
    event = create_tool_use_event("git mv file.txt ../outside.txt")
    results = list(git_mv_rule(event))
    assert len(results) == 1
    assert results[0].action == "deny"
