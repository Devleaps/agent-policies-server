"""Tests for trash command safe path enforcement."""

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


def test_trash_absolute_path_blocked(create_tool_use_event):
    """trash with absolute path should be blocked."""
    event = create_tool_use_event("trash /etc/hosts")
    results = list(whitelist_safe_paths_rule(event))
    assert len(results) == 1
    assert results[0].action == "deny"
    assert "absolute paths are not allowed" in results[0].reason


def test_trash_root_blocked(create_tool_use_event):
    """trash / should be blocked."""
    event = create_tool_use_event("trash /")
    results = list(whitelist_safe_paths_rule(event))
    assert len(results) == 1
    assert results[0].action == "deny"
    assert "absolute paths are not allowed" in results[0].reason


def test_trash_tmp_blocked(create_tool_use_event):
    """trash /tmp/ should be blocked (caught by absolute path check)."""
    event = create_tool_use_event("trash /tmp/file.txt")
    results = list(whitelist_safe_paths_rule(event))
    assert len(results) == 1
    assert results[0].action == "deny"
    assert "absolute paths are not allowed" in results[0].reason


def test_trash_tilde_blocked(create_tool_use_event):
    """trash with tilde path should be blocked."""
    event = create_tool_use_event("trash ~/Documents/file.txt")
    results = list(whitelist_safe_paths_rule(event))
    assert len(results) == 1
    assert results[0].action == "deny"
    assert "tilde-based paths (~) are not allowed" in results[0].reason


def test_trash_parent_dir_blocked(create_tool_use_event):
    """trash with ../ should be blocked."""
    event = create_tool_use_event("trash ../file.txt")
    results = list(whitelist_safe_paths_rule(event))
    assert len(results) == 1
    assert results[0].action == "deny"
    assert "upward directory traversal" in results[0].reason


def test_trash_parent_dir_in_path_blocked(create_tool_use_event):
    """trash with ../ in middle of path should be blocked."""
    event = create_tool_use_event("trash foo/../bar/file.txt")
    results = list(whitelist_safe_paths_rule(event))
    assert len(results) == 1
    assert results[0].action == "deny"
    assert "upward directory traversal" in results[0].reason


def test_trash_relative_path_allowed(create_tool_use_event):
    """trash with safe relative path should be allowed."""
    event = create_tool_use_event("trash file.txt")
    results = list(whitelist_safe_paths_rule(event))
    assert len(results) == 1
    assert results[0].action == "allow"


def test_trash_subdirectory_allowed(create_tool_use_event):
    """trash with safe subdirectory path should be allowed."""
    event = create_tool_use_event("trash src/components/Button.tsx")
    results = list(whitelist_safe_paths_rule(event))
    assert len(results) == 1
    assert results[0].action == "allow"


def test_trash_multiple_files_relative_allowed(create_tool_use_event):
    """trash with multiple relative files should be allowed."""
    event = create_tool_use_event("trash file1.txt file2.txt")
    results = list(whitelist_safe_paths_rule(event))
    assert len(results) == 1
    assert results[0].action == "allow"


def test_trash_wildcard_relative_allowed(create_tool_use_event):
    """trash with wildcard in relative path should be allowed."""
    event = create_tool_use_event("trash *.log")
    results = list(whitelist_safe_paths_rule(event))
    assert len(results) == 1
    assert results[0].action == "allow"


def test_trash_with_flags_relative_allowed(create_tool_use_event):
    """trash with flags and relative path should be allowed."""
    event = create_tool_use_event("trash -v file.txt")
    results = list(whitelist_safe_paths_rule(event))
    assert len(results) == 1
    assert results[0].action == "allow"
