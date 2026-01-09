"""Tests for pytest requiring uv run."""

import pytest
from devleaps.policies.server.common.models import ToolUseEvent
from devleaps.policies.server.common.enums import SourceClient
from src.python_uv.uv_tools_deny import uv_tools_direct_deny_rule
from src.python_uv.uv_tools_allow import uv_tools_run_allow_rule


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


def test_direct_pytest_denied(create_tool_use_event):
    """Direct pytest should be denied."""
    event = create_tool_use_event("pytest tests/")
    results = list(uv_tools_direct_deny_rule(event))
    assert len(results) == 1
    assert results[0].action == "deny"
    assert "uv run pytest" in results[0].reason


def test_uv_run_pytest_allowed(create_tool_use_event):
    """uv run pytest should be allowed."""
    event = create_tool_use_event("uv run pytest tests/")
    results = list(uv_tools_run_allow_rule(event))
    assert len(results) == 1
    assert results[0].action == "allow"


def test_pytest_with_flags_denied(create_tool_use_event):
    """Direct pytest with flags should be denied."""
    event = create_tool_use_event("pytest -v tests/test_something.py")
    results = list(uv_tools_direct_deny_rule(event))
    assert len(results) == 1
    assert results[0].action == "deny"


def test_uv_run_pytest_with_flags_allowed(create_tool_use_event):
    """uv run pytest with flags should be allowed."""
    event = create_tool_use_event("uv run pytest -v tests/")
    results = list(uv_tools_run_allow_rule(event))
    assert len(results) == 1
    assert results[0].action == "allow"
