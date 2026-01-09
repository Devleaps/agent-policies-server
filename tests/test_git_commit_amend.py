"""Tests for git commit --amend and --no-edit policy."""

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


def test_git_commit_amend_allowed(create_tool_use_event):
    """Allow git commit --amend without -m flag."""
    event = create_tool_use_event("git commit --amend")
    results = list(git_commit_rule(event))
    assert len(results) == 1
    assert results[0].action == "allow"


def test_git_commit_amend_no_edit_allowed(create_tool_use_event):
    """Allow git commit --amend --no-edit."""
    event = create_tool_use_event("git commit --amend --no-edit")
    results = list(git_commit_rule(event))
    assert len(results) == 1
    assert results[0].action == "allow"


def test_git_commit_with_other_flags_denied(create_tool_use_event):
    """Deny git commit with flags that aren't -m or --amend."""
    event = create_tool_use_event("git commit -a")
    results = list(git_commit_rule(event))
    assert len(results) == 1
    assert results[0].action == "deny"


def test_git_commit_plain_denied(create_tool_use_event):
    """Deny plain git commit."""
    event = create_tool_use_event("git commit")
    results = list(git_commit_rule(event))
    assert len(results) == 1
    assert results[0].action == "deny"
