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
    check_policy(client, base_event, "git push --force", "deny")


def test_git_push_force_with_lease_allowed(client, base_event):
    check_policy(client, base_event, "git push --force-with-lease", "allow")


def test_git_init_outside_workspace_denied(client, base_event):
    check_policy(client, base_event, "git init /tmp/new-repo", "deny")


def test_git_stash(client, base_event):
    check_policy(client, base_event, "git stash", "allow")


def test_git_stash_pop(client, base_event):
    check_policy(client, base_event, "git stash pop", "allow")


def test_git_stash_list(client, base_event):
    check_policy(client, base_event, "git stash list", "allow")


def test_git_remote(client, base_event):
    check_policy(client, base_event, "git remote", "allow")


def test_git_remote_verbose(client, base_event):
    check_policy(client, base_event, "git remote -v", "allow")


def test_git_remote_verbose_piped(client, base_event):
    check_policy(client, base_event, "git remote -v 2>/dev/null | head -5", "allow")


def test_git_remote_get_url(client, base_event):
    check_policy(client, base_event, "git remote get-url origin", "allow")


def test_git_remote_show(client, base_event):
    check_policy(client, base_event, "git remote show origin", "allow")


def test_git_remote_write_operations(client, base_event):
    """git remote write operations defer to user (no explicit policy)"""
    check_policy(
        client,
        base_event,
        "git remote add upstream https://github.com/user/repo.git",
        None,
    )
    check_policy(client, base_event, "git remote remove origin", None)
    check_policy(
        client,
        base_event,
        "git remote set-url origin https://github.com/new/repo.git",
        None,
    )
    check_policy(client, base_event, "git remote rename old new", None)


def test_git_with_c_safe_path(client, base_event):
    check_policy(client, base_event, "git -C agent-skills status", "allow")


def test_git_with_c_relative_safe_path(client, base_event):
    check_policy(client, base_event, "git -C ./subdir remote -v", "allow")


def test_git_with_c_unsafe_path_denied(client, base_event):
    check_policy(client, base_event, "git -C /tmp/agent-skills status", "deny")


def test_git_with_c_parent_path_denied(client, base_event):
    check_policy(client, base_event, "git -C ../other-repo status", "deny")
