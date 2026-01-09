"""Tests for git rm blocking policy."""

import pytest
from devleaps.policies.server.common.models import ToolUseEvent
from devleaps.policies.server.common.enums import SourceClient
from src.git.git_policy import git_rm_rule


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


def test_git_rm_file_denied(create_tool_use_event):
    """Block git rm with file."""
    event = create_tool_use_event("git rm file.txt")
    results = list(git_rm_rule(event))
    assert len(results) == 1
    assert results[0].action == "deny"


def test_git_rm_recursive_denied(create_tool_use_event):
    """Block git rm with -r flag."""
    event = create_tool_use_event("git rm -r directory/")
    results = list(git_rm_rule(event))
    assert len(results) == 1
    assert results[0].action == "deny"


def test_git_rm_cached_denied(create_tool_use_event):
    """Block git rm with --cached flag."""
    event = create_tool_use_event("git rm --cached file.txt")
    results = list(git_rm_rule(event))
    assert len(results) == 1
    assert results[0].action == "deny"


def test_git_rm_force_denied(create_tool_use_event):
    """Block git rm with -f flag."""
    event = create_tool_use_event("git rm -f file.txt")
    results = list(git_rm_rule(event))
    assert len(results) == 1
    assert results[0].action == "deny"
