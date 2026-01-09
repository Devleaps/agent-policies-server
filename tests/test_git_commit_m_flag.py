"""Tests for git commit -m flag policy."""

import pytest
from devleaps.policies.server.common.models import ToolUseEvent
from devleaps.policies.server.common.enums import SourceClient
from src.git.git_policy import git_commit_rule


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


def test_git_commit_with_m_flag_allowed(create_tool_use_event):
    """Allow git commit with -m flag."""
    event = create_tool_use_event('git commit -m "message"')
    results = list(git_commit_rule(event))
    assert len(results) == 1
    assert results[0].action == "allow"


def test_git_commit_amend_with_m_flag_allowed(create_tool_use_event):
    """Allow git commit --amend with -m flag (fix false positive)."""
    event = create_tool_use_event('git commit --amend -m "message"')
    results = list(git_commit_rule(event))
    assert len(results) == 1
    assert results[0].action == "allow"


def test_git_commit_without_m_flag_denied(create_tool_use_event):
    """Block git commit without -m flag."""
    event = create_tool_use_event("git commit")
    results = list(git_commit_rule(event))
    assert len(results) == 1
    assert results[0].action == "deny"


def test_git_commit_with_other_flags_but_no_m_denied(create_tool_use_event):
    """Block git commit with flags but no -m."""
    event = create_tool_use_event("git commit -a")
    results = list(git_commit_rule(event))
    assert len(results) == 1
    assert results[0].action == "deny"
