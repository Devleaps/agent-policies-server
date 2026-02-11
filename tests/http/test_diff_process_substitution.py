"""Test that diff with process substitution is allowed"""

from tests.http.conftest import check_policy


def test_diff_with_process_substitution_allowed(client, base_event):
    """Process substitution in diff command should be allowed"""
    cmd = 'diff <(ls | grep "^agent-" | sort) <(gh repo list Devleaps --limit 1000 --json name --jq \'.[] | .name\' | grep "^agent-" | sort) && echo "✅"'
    check_policy(client, base_event, cmd, "allow")


def test_dangerous_command_in_process_substitution_denied(client, base_event):
    """Dangerous commands inside process substitutions should be denied"""
    cmd = "diff <(cat safe.txt) <(sudo ls)"
    check_policy(client, base_event, cmd, "deny")


def test_dangerous_command_with_semicolon_in_process_substitution_denied(
    client, base_event
):
    """Semicolon works in process substitutions and policies still apply"""
    cmd = "diff <(ls ; sudo rm file.txt)"
    check_policy(client, base_event, cmd, "deny")
