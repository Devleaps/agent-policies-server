"""Tests for rm command trash guidance."""

import pytest
from devleaps.policies.server.common.models import ToolUseEvent
from devleaps.policies.server.common.enums import SourceClient
from src.universal.rm_allow import rm_safe_operations_rule


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


def test_rm_with_flags_mentions_trash(create_tool_use_event):
    """rm with flags should mention trash."""
    event = create_tool_use_event("rm -rf directory/")
    results = list(rm_safe_operations_rule(event))
    assert len(results) == 1
    assert results[0].action == "deny"
    assert "trash" in results[0].reason.lower()


def test_rm_with_absolute_path_mentions_trash(create_tool_use_event):
    """rm with absolute path should yield two denies."""
    event = create_tool_use_event("rm /tmp/file.txt")
    results = list(rm_safe_operations_rule(event))
    assert len(results) == 2
    assert results[0].action == "deny"
    assert "trash" in results[0].reason.lower()
    assert results[1].action == "deny"
    assert results[1].reason == "Absolute paths are not allowed."


def test_rm_root_yields_two_denies(create_tool_use_event):
    """rm -rf / should yield two denies."""
    event = create_tool_use_event("rm -rf /")
    results = list(rm_safe_operations_rule(event))
    assert len(results) == 2
    assert results[0].action == "deny"
    assert "trash" in results[0].reason.lower()
    assert results[1].action == "deny"
    assert results[1].reason == "Absolute paths are not allowed."


def test_rm_safe_path_denied(create_tool_use_event):
    """rm with safe relative path should be denied."""
    event = create_tool_use_event("rm file.txt")
    results = list(rm_safe_operations_rule(event))
    assert len(results) == 1
    assert results[0].action == "deny"
    assert "trash" in results[0].reason.lower()
