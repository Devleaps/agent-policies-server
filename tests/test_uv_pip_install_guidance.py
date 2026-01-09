"""Tests for uv pip install blocking."""

import pytest
from devleaps.policies.server.common.models import ToolUseEvent
from devleaps.policies.server.common.enums import SourceClient
from src.python_uv.uv_pip_install_guidance import uv_pip_install_deny_rule


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


def test_uv_pip_install_denied(create_tool_use_event):
    """uv pip install should be denied with suggestion to use uv add."""
    event = create_tool_use_event("uv pip install requests")
    results = list(uv_pip_install_deny_rule(event))

    assert len(results) == 1
    assert results[0].action == "deny"
    assert "uv add" in results[0].reason


def test_uv_pip_install_package_with_version_denied(create_tool_use_event):
    """uv pip install with version should be denied."""
    event = create_tool_use_event("uv pip install requests==2.28.0")
    results = list(uv_pip_install_deny_rule(event))

    assert len(results) == 1
    assert results[0].action == "deny"


def test_uv_pip_other_commands_match_no_policies(create_tool_use_event):
    """uv pip commands other than install should match no policies."""
    event = create_tool_use_event("uv pip list")
    results = list(uv_pip_install_deny_rule(event))
    assert len(results) == 0
