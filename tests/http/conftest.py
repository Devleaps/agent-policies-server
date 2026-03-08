"""
Shared fixtures and helpers for HTTP integration tests
"""

import pytest
from fastapi.testclient import TestClient

from src.server.server import app


@pytest.fixture
def client():
    """FastAPI test client for making HTTP requests"""
    return TestClient(app)


@pytest.fixture
def base_event():
    """Base Claude Code PreToolUse event structure"""
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


def check_policy(client, base_event, command, expected_decision):
    """Helper to check policy decision for a Bash command.

    Pass expected_decision=None to assert that no permissionDecision is returned
    (i.e. the server defers to the user's own permission system).
    """
    base_event["event"]["tool_input"]["command"] = command
    response = client.post("/policy/claude-code/PreToolUse", json=base_event)
    assert response.status_code == 200
    data = response.json()
    if expected_decision is None:
        assert "permissionDecision" not in data.get("hookSpecificOutput", {})
    else:
        assert data["hookSpecificOutput"]["permissionDecision"] == expected_decision
    return data
