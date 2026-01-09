"""Tests for uv python execution rules."""

import pytest
from devleaps.policies.server.common.models import ToolUseEvent
from devleaps.policies.server.common.enums import SourceClient
from src.python_uv.uv_python_deny import (
    uv_python_direct_deny_rule,
    uv_python_run_escape_deny_rule
)


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


def test_python_script_denied(create_tool_use_event):
    """Block python script.py and suggest uv run."""
    event = create_tool_use_event("python script.py")
    results = list(uv_python_direct_deny_rule(event))
    assert len(results) == 1
    assert results[0].action == "deny"
    assert "uv run script.py" in results[0].reason


def test_python_m_pytest_denied(create_tool_use_event):
    """Block python -m pytest and suggest uv run pytest."""
    event = create_tool_use_event("python -m pytest")
    results = list(uv_python_direct_deny_rule(event))
    assert len(results) == 1
    assert results[0].action == "deny"
    assert "uv run pytest" in results[0].reason


def test_python3_m_module_denied(create_tool_use_event):
    """Block python3 -m module and suggest uv run module."""
    event = create_tool_use_event("python3 -m mymodule")
    results = list(uv_python_direct_deny_rule(event))
    assert len(results) == 1
    assert results[0].action == "deny"
    assert "uv run mymodule" in results[0].reason


def test_python_scripts_folder_asks(create_tool_use_event):
    """Ask user for python scripts/something.py."""
    event = create_tool_use_event("python scripts/something.py")
    results = list(uv_python_direct_deny_rule(event))
    assert len(results) == 1
    assert results[0].action == "ask"


def test_uv_run_python_denied(create_tool_use_event):
    """Block uv run python and suggest pytest or scripts folder."""
    event = create_tool_use_event("uv run python script.py")
    results = list(uv_python_run_escape_deny_rule(event))
    assert len(results) == 1
    assert results[0].action == "deny"
    assert "pytest" in results[0].reason or "scripts/" in results[0].reason
