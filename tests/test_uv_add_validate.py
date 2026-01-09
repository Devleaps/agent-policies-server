"""Tests for uv add PyPI validation."""

import pytest
from devleaps.policies.server.common.models import ToolUseEvent
from devleaps.policies.server.common.enums import SourceClient
from src.python_uv.uv_add_validate import uv_add_validate_rule, is_package_allowed


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


def test_old_package_allowed(create_tool_use_event):
    """uv add with old popular package should be allowed."""
    event = create_tool_use_event("uv add requests")
    results = list(uv_add_validate_rule(event))
    assert len(results) == 1
    assert results[0].action == "allow"
    assert "year" in results[0].reason.lower()


def test_old_package_httpx_allowed(create_tool_use_event):
    """uv add httpx should be allowed (old package)."""
    event = create_tool_use_event("uv add httpx")
    results = list(uv_add_validate_rule(event))
    assert len(results) == 1
    assert results[0].action == "allow"


def test_nonexistent_package_denied(create_tool_use_event):
    """uv add with non-existent package should be denied."""
    event = create_tool_use_event("uv add this-package-definitely-does-not-exist-12345")
    results = list(uv_add_validate_rule(event))
    assert len(results) == 1
    assert results[0].action == "deny"
    assert "not found" in results[0].reason.lower()


def test_is_package_allowed_requests():
    """Direct test of is_package_allowed for requests."""
    allowed, reason = is_package_allowed("requests")
    assert allowed is True
    assert "year" in reason.lower()


def test_is_package_allowed_nonexistent():
    """Direct test of is_package_allowed for non-existent package."""
    allowed, reason = is_package_allowed("this-does-not-exist-12345")
    assert allowed is False
    assert "not found" in reason.lower() or "failed" in reason.lower()
