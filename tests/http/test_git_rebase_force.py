"""
HTTP Integration Tests for git rebase progress flags and the force-push
denial pointing at --force-with-lease.
"""

import pytest

from tests.http.conftest import check_policy


@pytest.mark.parametrize("flag", ["--continue", "--abort", "--skip", "--quit"])
def test_git_rebase_progress_allowed(client, base_event, flag):
    check_policy(client, base_event, f"git rebase {flag}", "allow")


def test_git_rebase_onto_branch_defers_to_user(client, base_event):
    check_policy(client, base_event, "git rebase main", None)


def test_git_rebase_interactive_defers_to_user(client, base_event):
    check_policy(client, base_event, "git rebase -i main", None)


def test_git_rebase_continue_with_extra_argument_defers_to_user(client, base_event):
    check_policy(client, base_event, "git rebase --continue main", None)


def test_git_push_force_denial_points_at_force_with_lease(client, base_event):
    data = check_policy(client, base_event, "git push --force origin main", "deny")
    reason = data["hookSpecificOutput"]["permissionDecisionReason"]
    assert "--force-with-lease" in reason


def test_git_push_force_with_lease_allowed(client, base_event):
    check_policy(client, base_event, "git push --force-with-lease origin main", "allow")
