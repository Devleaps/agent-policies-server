"""Tests for blocking absolute path executables."""

import pytest
from devleaps.policies.server.common.models import ToolUseEvent
from devleaps.policies.server.common.enums import SourceClient
from src.universal.absolute_path_executables import absolute_path_executable_rule


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


def test_absolute_path_executable_denied(create_tool_use_event):
    """Absolute path executables should be denied."""
    event = create_tool_use_event("/usr/bin/python script.py")
    results = list(absolute_path_executable_rule(event))
    assert len(results) == 1
    assert results[0].action == "deny"


def test_venv_bin_executable_denied(create_tool_use_event):
    """.venv/bin executables should be denied."""
    event = create_tool_use_event(".venv/bin/pytest tests/")
    results = list(absolute_path_executable_rule(event))
    assert len(results) == 1
    assert results[0].action == "deny"


def test_absolute_venv_path_denied(create_tool_use_event):
    """Absolute paths with .venv should be denied."""
    event = create_tool_use_event("/Users/username/project/.venv/bin/pytest tests/")
    results = list(absolute_path_executable_rule(event))
    assert len(results) == 1
    assert results[0].action == "deny"


def test_relative_command_match_no_policies(create_tool_use_event):
    """Relative commands should match no policies."""
    event = create_tool_use_event("pytest tests/")
    results = list(absolute_path_executable_rule(event))
    assert len(results) == 0


def test_dot_slash_relative_match_no_policies(create_tool_use_event):
    """./relative paths should match no policies."""
    event = create_tool_use_event("./script.sh arg1 arg2")
    results = list(absolute_path_executable_rule(event))
    assert len(results) == 0
