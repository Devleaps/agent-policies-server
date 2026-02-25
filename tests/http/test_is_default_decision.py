"""
Tests for PreToolUse fallback behaviour when no policy rule matches.

When no policy rule has an opinion on a tool use, the server omits
permissionDecision entirely. Claude Code then falls back to its own native
permission system (allowedTools, settings files, interactive dialog).

When a policy rule explicitly produces a decision, permissionDecision must be
present in the response so Claude Code honours the server's explicit verdict.
"""

import pytest
from fastapi.testclient import TestClient

from src.server.server import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def bash_event():
    return {
        "event": {
            "session_id": "test-session",
            "transcript_path": "/tmp/transcript.jsonl",
            "cwd": "/workspace",
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": ""},
            "tool_use_id": "toolu_test",
        },
        "bundles": ["universal"],
    }


def test_unknown_command_has_no_permission_decision(client, bash_event):
    """When no policy rule matches, permissionDecision must be absent."""
    bash_event["event"]["tool_input"]["command"] = "some-completely-unknown-command"
    response = client.post("/policy/claude-code/PreToolUse", json=bash_event)
    assert response.status_code == 200
    data = response.json()
    assert "permissionDecision" not in data.get("hookSpecificOutput", {})


def test_empty_command_has_no_permission_decision(client, bash_event):
    """An empty command has no matching policy rule, so permissionDecision is absent."""
    bash_event["event"]["tool_input"]["command"] = ""
    response = client.post("/policy/claude-code/PreToolUse", json=bash_event)
    assert response.status_code == 200
    data = response.json()
    assert "permissionDecision" not in data.get("hookSpecificOutput", {})


def test_denied_command_has_permission_decision(client, bash_event):
    """When a policy rule explicitly denies, permissionDecision must be present."""
    bash_event["event"]["tool_input"]["command"] = "sudo apt-get update"
    response = client.post("/policy/claude-code/PreToolUse", json=bash_event)
    assert response.status_code == 200
    data = response.json()
    assert data["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_allowed_command_has_permission_decision(client, bash_event):
    """When a policy rule explicitly allows, permissionDecision must be present."""
    bash_event["event"]["tool_input"]["command"] = "pwd"
    response = client.post("/policy/claude-code/PreToolUse", json=bash_event)
    assert response.status_code == 200
    data = response.json()
    assert data["hookSpecificOutput"]["permissionDecision"] == "allow"


def test_non_bash_tool_has_no_permission_decision(client, bash_event):
    """Non-Bash tools with no matching rule also omit permissionDecision."""
    bash_event["event"]["tool_name"] = "Read"
    bash_event["event"]["tool_input"] = {"file_path": "/workspace/src/main.py"}
    response = client.post("/policy/claude-code/PreToolUse", json=bash_event)
    assert response.status_code == 200
    data = response.json()
    assert "permissionDecision" not in data.get("hookSpecificOutput", {})
