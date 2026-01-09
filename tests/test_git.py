import pytest
from src.git.git_policy import (
    git_add_rule,
    git_commit_rule,
    git_mv_rule,
    git_push_force_rule,
    git_rm_rule
)
from tests.helpers import assert_allow, assert_deny, assert_pass


def test_git_add(bash_event):
    assert_allow(git_add_rule, bash_event("git add -A"))
    assert_allow(git_add_rule, bash_event("git add file.txt"))
    assert_allow(git_add_rule, bash_event("git add src/file.py"))
    assert_allow(git_add_rule, bash_event("git add file1.txt file2.txt"))


def test_git_commit(bash_event):
    assert_allow(git_commit_rule, bash_event('git commit -m "message"'))
    assert_allow(git_commit_rule, bash_event('git commit --amend -m "message"'))
    assert_allow(git_commit_rule, bash_event("git commit --amend"))
    assert_allow(git_commit_rule, bash_event("git commit --amend --no-edit"))
    assert_deny(git_commit_rule, bash_event("git commit"))
    assert_deny(git_commit_rule, bash_event("git commit -a"))


def test_git_mv(bash_event):
    assert_allow(git_mv_rule, bash_event("git mv oldfile.txt newfile.txt"))
    assert_allow(git_mv_rule, bash_event("git mv -f src/old.py src/new.py"))
    assert_deny(git_mv_rule, bash_event("git mv /tmp/file.txt local.txt"))
    assert_deny(git_mv_rule, bash_event("git mv file.txt ../outside.txt"))


def test_git_push_force(bash_event):
    assert_deny(git_push_force_rule, bash_event("git push --force"))
    assert_deny(git_push_force_rule, bash_event("git push -f"))
    assert_deny(git_push_force_rule, bash_event("git push --force origin main"))
    assert_deny(git_push_force_rule, bash_event("git push -f origin main"))


def test_git_rm(bash_event):
    assert_deny(git_rm_rule, bash_event("git rm file.txt"))
    assert_deny(git_rm_rule, bash_event("git rm -r directory/"))
    assert_deny(git_rm_rule, bash_event("git rm --cached file.txt"))
    assert_deny(git_rm_rule, bash_event("git rm -f file.txt"))
