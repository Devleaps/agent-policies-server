"""
HTTP Integration Tests for Gemini BeforeTool Hook
"""

import pytest
from fastapi.testclient import TestClient

from src.server.server import app


@pytest.fixture
def client():
    """FastAPI test client for making HTTP requests."""
    return TestClient(app)


@pytest.fixture
def gemini_base_event():
    """Base Gemini BeforeTool event structure for run_shell_command."""
    return {
        "bundles": ["universal"],
        "default_policy_behavior": "ask",
        "event": {
            "session_id": "test-gemini-session",
            "hook_event_name": "BeforeTool",
            "tool_name": "run_shell_command",
            "tool_input": {"command": ""},
            "cwd": "/workspace",
        },
    }


def check_gemini_policy(client, event, command, expected_decision):
    """Helper to check Gemini policy decision for a run_shell_command tool call."""
    event["event"]["tool_input"]["command"] = command
    response = client.post("/policy/gemini/BeforeTool", json=event)
    assert response.status_code == 200
    data = response.json()
    assert data.get("decision") == expected_decision
    return data


def test_pwd_is_allowed(client, gemini_base_event):
    check_gemini_policy(client, gemini_base_event, "pwd", "allow")


def test_git_status_is_allowed(client, gemini_base_event):
    check_gemini_policy(client, gemini_base_event, "git status", "allow")


def test_sudo_is_denied(client, gemini_base_event):
    check_gemini_policy(client, gemini_base_event, "sudo apt-get update", "deny")


def test_rm_rf_is_denied(client, gemini_base_event):
    check_gemini_policy(client, gemini_base_event, "rm -rf /data", "deny")


def test_unknown_command_returns_no_decision(client, gemini_base_event):
    """Unknown commands yield no decision; Gemini applies its own default_policy_behavior."""
    check_gemini_policy(client, gemini_base_event, "some-completely-unknown-command", None)


def test_deny_includes_reason(client, gemini_base_event):
    data = check_gemini_policy(client, gemini_base_event, "sudo rm -rf /", "deny")
    assert data.get("reason") is not None
    assert len(data["reason"]) > 0


def test_non_bash_tool_returns_no_decision(client, gemini_base_event):
    """Non-shell tools are not matched as bash and yield no decision."""
    gemini_base_event["event"]["tool_name"] = "read_file"
    gemini_base_event["event"]["tool_input"] = {"path": "/workspace/README.md"}
    response = client.post("/policy/gemini/BeforeTool", json=gemini_base_event)
    assert response.status_code == 200
    data = response.json()
    assert data.get("decision") is None


def test_before_tool_returns_200(client, gemini_base_event):
    """BeforeTool endpoint is reachable and returns a valid response."""
    gemini_base_event["event"]["tool_input"]["command"] = "pwd"
    response = client.post("/policy/gemini/BeforeTool", json=gemini_base_event)
    assert response.status_code == 200


def test_after_tool_returns_200(client):
    """AfterTool endpoint is reachable and returns a valid response."""
    event = {
        "bundles": ["universal"],
        "default_policy_behavior": "ask",
        "event": {
            "session_id": "test-gemini-session",
            "hook_event_name": "AfterTool",
            "tool_name": "run_shell_command",
            "tool_input": {"command": "pwd"},
            "cwd": "/workspace",
            "tool_response": {"llmContent": "/workspace\n", "returnDisplay": "/workspace\n"},
        },
    }
    response = client.post("/policy/gemini/AfterTool", json=event)
    assert response.status_code == 200


def test_uv_sync_without_bundle_returns_no_decision(client, gemini_base_event):
    """Unknown uv command without bundle yields no decision (not deny or allow)."""
    gemini_base_event["bundles"] = ["universal"]
    check_gemini_policy(client, gemini_base_event, "uv sync", None)


def test_uv_sync_with_bundle_is_allowed(client, gemini_base_event):
    gemini_base_event["bundles"] = ["universal", "python_uv"]
    check_gemini_policy(client, gemini_base_event, "uv sync", "allow")
