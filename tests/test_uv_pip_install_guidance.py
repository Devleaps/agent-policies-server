"""Tests for uv pip install guidance."""

import pytest
from devleaps.policies.server.common.models import ToolUseEvent
from devleaps.policies.server.common.enums import SourceClient
from src.python_uv.uv_pip_install_guidance import uv_pip_install_guidance_rule


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


def test_uv_pip_install_triggers_guidance(create_tool_use_event):
    """uv pip install should trigger guidance to use uv add."""
    event = create_tool_use_event("uv pip install requests")
    results = list(uv_pip_install_guidance_rule(event))

    # Should yield allow + guidance
    decisions = [r for r in results if hasattr(r, 'action')]
    guidance = [r for r in results if hasattr(r, 'content')]

    assert len(decisions) == 1
    assert decisions[0].action == "allow"
    assert len(guidance) == 1
    assert "uv add" in guidance[0].content


def test_uv_pip_install_package_with_version(create_tool_use_event):
    """uv pip install with version should trigger guidance."""
    event = create_tool_use_event("uv pip install requests==2.28.0")
    results = list(uv_pip_install_guidance_rule(event))

    guidance = [r for r in results if hasattr(r, 'content')]
    assert len(guidance) == 1


def test_uv_pip_other_commands_no_guidance(create_tool_use_event):
    """uv pip commands other than install should not trigger guidance."""
    event = create_tool_use_event("uv pip list")
    results = list(uv_pip_install_guidance_rule(event))
    assert len(results) == 0
