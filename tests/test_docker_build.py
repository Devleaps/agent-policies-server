"""Tests for docker build policy."""

import pytest
from devleaps.policies.server.common.models import ToolUseEvent
from devleaps.policies.server.common.enums import SourceClient
from src.cloud.docker_build import docker_build_rule


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


def test_docker_build_current_dir_allowed(create_tool_use_event):
    """docker build . should be allowed."""
    event = create_tool_use_event("docker build .")
    results = list(docker_build_rule(event))
    assert len(results) == 1
    assert results[0].action == "allow"


def test_docker_build_with_tag_allowed(create_tool_use_event):
    """docker build -t name . should be allowed."""
    event = create_tool_use_event("docker build -t agent-policy-server .")
    results = list(docker_build_rule(event))
    assert len(results) == 1
    assert results[0].action == "allow"


def test_docker_build_with_tag_version_allowed(create_tool_use_event):
    """docker build -t name:tag . should be allowed."""
    event = create_tool_use_event("docker build -t myapp:1.0.0 .")
    results = list(docker_build_rule(event))
    assert len(results) == 1
    assert results[0].action == "allow"


def test_docker_build_subdir_allowed(create_tool_use_event):
    """docker build with relative subdir should be allowed."""
    event = create_tool_use_event("docker build -t app ./subdir")
    results = list(docker_build_rule(event))
    assert len(results) == 1
    assert results[0].action == "allow"


def test_docker_build_absolute_path_blocked(create_tool_use_event):
    """docker build with absolute path should be blocked."""
    event = create_tool_use_event("docker build -t app /home/user/project")
    results = list(docker_build_rule(event))
    assert len(results) == 1
    assert results[0].action == "deny"
    assert "absolute path" in results[0].reason.lower()


def test_docker_build_long_tag_allowed(create_tool_use_event):
    """docker build with --tag should be allowed."""
    event = create_tool_use_event("docker build --tag myapp:latest .")
    results = list(docker_build_rule(event))
    assert len(results) == 1
    assert results[0].action == "allow"
