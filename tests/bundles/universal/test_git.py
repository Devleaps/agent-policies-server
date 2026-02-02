import pytest
from src.evaluation import evaluate_bash_rules
from tests.helpers import assert_allow, assert_deny, assert_pass


def test_git_add(bash_event):
    assert_allow(evaluate_bash_rules, bash_event("git add -A"))
    assert_allow(evaluate_bash_rules, bash_event("git add file.txt"))
    assert_allow(evaluate_bash_rules, bash_event("git add src/file.py"))
    assert_allow(evaluate_bash_rules, bash_event("git add file1.txt file2.txt"))


def test_git_commit(bash_event):
    assert_allow(evaluate_bash_rules, bash_event('git commit -m "message"'))
    assert_allow(evaluate_bash_rules, bash_event('git commit --amend -m "message"'))
    assert_allow(evaluate_bash_rules, bash_event("git commit --amend"))
    assert_allow(evaluate_bash_rules, bash_event("git commit --amend --no-edit"))
    assert_deny(evaluate_bash_rules, bash_event("git commit"))
    assert_deny(evaluate_bash_rules, bash_event("git commit -a"))


def test_git_mv(bash_event):
    assert_allow(evaluate_bash_rules, bash_event("git mv oldfile.txt newfile.txt"))
    assert_allow(evaluate_bash_rules, bash_event("git mv -f src/old.py src/new.py"))
    assert_deny(evaluate_bash_rules, bash_event("git mv /tmp/file.txt local.txt"))
    assert_deny(evaluate_bash_rules, bash_event("git mv file.txt ../outside.txt"))


def test_git_push_force(bash_event):
    assert_deny(evaluate_bash_rules, bash_event("git push --force"))
    assert_deny(evaluate_bash_rules, bash_event("git push -f"))
    assert_deny(evaluate_bash_rules, bash_event("git push --force origin main"))
    assert_deny(evaluate_bash_rules, bash_event("git push -f origin main"))


def test_git_rm(bash_event):
    assert_deny(evaluate_bash_rules, bash_event("git rm file.txt"))
    assert_deny(evaluate_bash_rules, bash_event("git rm -r directory/"))
    assert_deny(evaluate_bash_rules, bash_event("git rm --cached file.txt"))
    assert_deny(evaluate_bash_rules, bash_event("git rm -f file.txt"))


def test_git_with_c_option_safe_paths(bash_event):
    """Test git -C with safe relative paths."""
    assert_allow(evaluate_bash_rules, bash_event("git -C src status"))
    assert_allow(evaluate_bash_rules, bash_event('git -C subdir commit -m "message"'))
    assert_allow(evaluate_bash_rules, bash_event("git -C agent-skills remote -v"))


def test_git_with_c_option_unsafe_paths(bash_event):
    """Test git -C with unsafe paths."""
    assert_deny(evaluate_bash_rules, bash_event("git -C /absolute/path status"))
    assert_deny(evaluate_bash_rules, bash_event("git -C ../parent status"))
    assert_deny(evaluate_bash_rules, bash_event("git -C /tmp/repo status"))


def test_git_branch_read_only(bash_event):
    assert_allow(evaluate_bash_rules, bash_event("git branch"))
    assert_allow(evaluate_bash_rules, bash_event("git branch -a"))
    assert_allow(evaluate_bash_rules, bash_event("git branch -r"))
    assert_allow(evaluate_bash_rules, bash_event("git branch -v"))
    assert_allow(evaluate_bash_rules, bash_event("git branch --list"))
    assert_allow(evaluate_bash_rules, bash_event("git branch --all"))
    assert_allow(evaluate_bash_rules, bash_event("git branch --remotes"))


def test_git_branch_local_operations(bash_event):
    assert_allow(evaluate_bash_rules, bash_event("git branch new-feature"))
    assert_allow(evaluate_bash_rules, bash_event("git branch bugfix/issue-123"))
    assert_allow(evaluate_bash_rules, bash_event("git branch -m old-name new-name"))
    assert_allow(evaluate_bash_rules, bash_event("git branch -m new-name"))
    assert_allow(evaluate_bash_rules, bash_event("git branch -d merged-branch"))


def test_git_branch_force_delete(bash_event):
    assert_deny(evaluate_bash_rules, bash_event("git branch -D old-branch"))


def test_git_ls_files(bash_event):
    assert_allow(evaluate_bash_rules, bash_event("git ls-files"))
    assert_allow(evaluate_bash_rules, bash_event("git ls-files -m"))
    assert_allow(evaluate_bash_rules, bash_event("git ls-files --cached"))


def test_git_reflog(bash_event):
    assert_allow(evaluate_bash_rules, bash_event("git reflog"))
    assert_allow(evaluate_bash_rules, bash_event("git reflog show"))
    assert_allow(evaluate_bash_rules, bash_event("git reflog --all"))


def test_git_init(bash_event):
    assert_allow(evaluate_bash_rules, bash_event("git init"))
    assert_allow(evaluate_bash_rules, bash_event("git init my-repo"))
    assert_allow(evaluate_bash_rules, bash_event("git init --bare"))


def test_git_stash(bash_event):
    """Test git stash operations."""
    assert_allow(evaluate_bash_rules, bash_event("git stash"))
    assert_allow(evaluate_bash_rules, bash_event("git stash list"))
    assert_allow(evaluate_bash_rules, bash_event("git stash show"))
    assert_allow(evaluate_bash_rules, bash_event("git stash push -m 'WIP'"))
    assert_allow(evaluate_bash_rules, bash_event("git stash pop"))
    assert_allow(evaluate_bash_rules, bash_event("git stash apply"))
    assert_allow(evaluate_bash_rules, bash_event("git stash drop"))
    assert_allow(evaluate_bash_rules, bash_event("git stash clear"))


def test_git_remote_read_only(bash_event):
    """Test git remote read-only operations."""
    assert_allow(evaluate_bash_rules, bash_event("git remote"))
    assert_allow(evaluate_bash_rules, bash_event("git remote -v"))
    assert_allow(evaluate_bash_rules, bash_event("git remote --verbose"))
    assert_allow(evaluate_bash_rules, bash_event("git remote show origin"))
    assert_allow(evaluate_bash_rules, bash_event("git remote get-url origin"))


def test_git_remote_with_pipes(bash_event):
    """Test git remote with piped commands."""
    assert_allow(evaluate_bash_rules, bash_event("git remote -v 2>/dev/null | head -5"))
