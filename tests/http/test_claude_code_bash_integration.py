"""
HTTP Integration Tests for Claude Code Bash Tool Use
"""

from tests.http.conftest import check_policy


def test_pwd_is_allowed(client, base_event):
    check_policy(client, base_event, "pwd", "allow")


def test_git_status_is_allowed(client, base_event):
    check_policy(client, base_event, "git status", "allow")


def test_ls_with_safe_path_is_allowed(client, base_event):
    check_policy(client, base_event, "ls src/", "allow")


def test_sudo_is_denied(client, base_event):
    check_policy(client, base_event, "sudo apt-get update", "deny")


def test_rm_rf_is_denied(client, base_event):
    check_policy(client, base_event, "rm -rf /important/data", "deny")


def test_kill_all_is_denied(client, base_event):
    check_policy(client, base_event, "killall python", "deny")


def test_path_traversal_is_denied(client, base_event):
    check_policy(client, base_event, "cat ../../etc/passwd", "deny")


def test_git_push_force_is_denied(client, base_event):
    check_policy(client, base_event, "git push --force", "deny")


def test_terraform_apply_is_denied(client, base_event):
    check_policy(client, base_event, "terraform apply", "deny")


def test_unknown_command_defers_to_user(client, base_event):
    check_policy(client, base_event, "some-completely-unknown-command", None)


def test_decision_precedence_deny_wins(client, base_event):
    check_policy(client, base_event, "sudo git status", "deny")


def test_unknown_command_defers_to_user_not_allow(client, base_event):
    check_policy(client, base_event, "some-random-unknown-tool", None)


def test_uv_sync_without_bundle_defers_to_user(client, base_event):
    base_event["bundles"] = ["universal"]
    check_policy(client, base_event, "uv sync", None)


def test_uv_sync_with_bundle_is_allowed(client, base_event):
    base_event["bundles"] = ["universal", "python_uv"]
    check_policy(client, base_event, "uv sync", "allow")


def test_empty_command_defers_to_user(client, base_event):
    check_policy(client, base_event, "", None)


def test_non_bash_tool_defers_to_user(client, base_event):
    base_event["event"]["tool_name"] = "Read"
    base_event["event"]["tool_input"] = {"file_path": "/some/file.txt"}
    response = client.post("/policy/claude-code/PreToolUse", json=base_event)
    assert response.status_code == 200
    assert "permissionDecision" not in response.json().get("hookSpecificOutput", {})


def test_deny_includes_reason(client, base_event):
    data = check_policy(client, base_event, "sudo rm -rf /", "deny")
    assert data["systemMessage"] is not None
    assert len(data["systemMessage"]) > 0
    assert data["hookSpecificOutput"]["permissionDecisionReason"] is not None
