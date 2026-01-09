"""Tests for gh api method GET requirement policy."""

import pytest
from devleaps.policies.server.common.models import ToolUseEvent
from devleaps.policies.server.common.enums import SourceClient
from src.cloud.gh_api import gh_api_rule


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


def test_gh_api_with_method_get_allowed(create_tool_use_event):
    """Allow gh api with --method GET."""
    event = create_tool_use_event("gh api --method GET /repos/owner/repo")
    results = list(gh_api_rule(event))
    assert len(results) == 1
    assert results[0].action == "allow"


def test_gh_api_with_method_get_after_path_allowed(create_tool_use_event):
    """Allow gh api with --method GET after path."""
    event = create_tool_use_event("gh api /repos/owner/repo --method GET")
    results = list(gh_api_rule(event))
    assert len(results) == 1
    assert results[0].action == "allow"


def test_gh_api_without_method_denied(create_tool_use_event):
    """Block gh api without --method GET."""
    event = create_tool_use_event("gh api /repos/owner/repo")
    results = list(gh_api_rule(event))
    assert len(results) == 1
    assert results[0].action == "deny"


def test_gh_api_with_method_post_denied(create_tool_use_event):
    """Block gh api with --method POST."""
    event = create_tool_use_event("gh api --method POST /repos/owner/repo/issues")
    results = list(gh_api_rule(event))
    assert len(results) == 1
    assert results[0].action == "deny"
