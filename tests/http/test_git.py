"""
HTTP Integration Tests for Git Commands
"""

from tests.http.conftest import check_policy


def test_git_add(client, base_event):
    check_policy(client, base_event, "git add .", "allow")


def test_git_add_with_flags(client, base_event):
    check_policy(client, base_event, "git add -A", "allow")


def test_git_commit(client, base_event):
    check_policy(client, base_event, "git commit -m 'test'", "allow")


def test_git_status(client, base_event):
    check_policy(client, base_event, "git status", "allow")


def test_git_diff(client, base_event):
    check_policy(client, base_event, "git diff", "allow")


def test_git_log(client, base_event):
    check_policy(client, base_event, "git log --oneline", "allow")


def test_git_branch(client, base_event):
    check_policy(client, base_event, "git branch feature-123", "allow")


def test_git_checkout(client, base_event):
    check_policy(client, base_event, "git checkout main", "allow")


def test_git_ls_files(client, base_event):
    check_policy(client, base_event, "git ls-files", "allow")


def test_git_mv(client, base_event):
    check_policy(client, base_event, "git mv old.txt new.txt", "allow")


def test_git_rm(client, base_event):
    check_policy(client, base_event, "git rm file.txt", "deny")


def test_git_reflog(client, base_event):
    check_policy(client, base_event, "git reflog", "allow")


def test_git_show(client, base_event):
    check_policy(client, base_event, "git show HEAD", "allow")


def test_git_push(client, base_event):
    check_policy(client, base_event, "git push origin main", "allow")


def test_git_push_force_denied(client, base_event):
    data = check_policy(client, base_event, "git push --force", "deny")
    assert "force" in data["hookSpecificOutput"]["permissionDecisionReason"].lower()


def test_git_push_force_with_lease_allowed(client, base_event):
    check_policy(client, base_event, "git push --force-with-lease", "allow")


def test_git_init_outside_workspace_denied(client, base_event):
    check_policy(client, base_event, "git init /tmp/new-repo", "deny")
