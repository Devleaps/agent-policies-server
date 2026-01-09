"""Tests for touch command policy."""

import pytest
from devleaps.policies.server.common.models import ToolUseEvent
from devleaps.policies.server.common.enums import SourceClient
from src.universal.whitelist_safe_paths import whitelist_safe_paths_rule


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


def test_touch_simple_file(create_tool_use_event):
    """Allow touch with simple filename."""
    event = create_tool_use_event("touch newfile.txt")
    results = list(whitelist_safe_paths_rule(event))
    assert len(results) == 1
    assert results[0].action == "allow"


def test_touch_with_flags(create_tool_use_event):
    """Allow touch with flags."""
    event = create_tool_use_event("touch -t 202301011200 file.txt")
    results = list(whitelist_safe_paths_rule(event))
    assert len(results) == 1
    assert results[0].action == "allow"


def test_touch_absolute_path_denied(create_tool_use_event):
    """Block touch with absolute path."""
    event = create_tool_use_event("touch /tmp/file.txt")
    results = list(whitelist_safe_paths_rule(event))
    assert len(results) == 1
    assert results[0].action == "deny"


def test_touch_parent_directory_denied(create_tool_use_event):
    """Block touch with parent directory traversal."""
    event = create_tool_use_event("touch ../file.txt")
    results = list(whitelist_safe_paths_rule(event))
    assert len(results) == 1
    assert results[0].action == "deny"
