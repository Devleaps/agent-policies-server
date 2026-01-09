"""Tests for git push --force blocking policy."""

import pytest
from devleaps.policies.server.common.models import ToolUseEvent
from devleaps.policies.server.common.enums import SourceClient
from src.git.git_policy import git_push_force_rule


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


def test_git_push_force_long_flag_denied(create_tool_use_event):
    """Block git push with --force flag."""
    event = create_tool_use_event("git push --force")
    results = list(git_push_force_rule(event))
    assert len(results) == 1
    assert results[0].action == "deny"


def test_git_push_force_short_flag_denied(create_tool_use_event):
    """Block git push with -f flag."""
    event = create_tool_use_event("git push -f")
    results = list(git_push_force_rule(event))
    assert len(results) == 1
    assert results[0].action == "deny"


def test_git_push_force_with_remote_denied(create_tool_use_event):
    """Block git push --force with remote and branch."""
    event = create_tool_use_event("git push --force origin main")
    results = list(git_push_force_rule(event))
    assert len(results) == 1
    assert results[0].action == "deny"


def test_git_push_f_with_remote_denied(create_tool_use_event):
    """Block git push -f with remote and branch."""
    event = create_tool_use_event("git push -f origin main")
    results = list(git_push_force_rule(event))
    assert len(results) == 1
    assert results[0].action == "deny"
