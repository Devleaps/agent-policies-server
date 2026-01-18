import pytest
from src.bundles_impl import bash_rules_bundle_universal
from tests.helpers import assert_allow, assert_deny, assert_pass


def test_git_add(bash_event):
    assert_allow(bash_rules_bundle_universal, bash_event("git add -A"))
    assert_allow(bash_rules_bundle_universal, bash_event("git add file.txt"))
    assert_allow(bash_rules_bundle_universal, bash_event("git add src/file.py"))
    assert_allow(bash_rules_bundle_universal, bash_event("git add file1.txt file2.txt"))


def test_git_commit(bash_event):
    assert_allow(bash_rules_bundle_universal, bash_event('git commit -m "message"'))
    assert_allow(bash_rules_bundle_universal, bash_event('git commit --amend -m "message"'))
    assert_allow(bash_rules_bundle_universal, bash_event("git commit --amend"))
    assert_allow(bash_rules_bundle_universal, bash_event("git commit --amend --no-edit"))
    assert_deny(bash_rules_bundle_universal, bash_event("git commit"))
    assert_deny(bash_rules_bundle_universal, bash_event("git commit -a"))


def test_git_mv(bash_event):
    assert_allow(bash_rules_bundle_universal, bash_event("git mv oldfile.txt newfile.txt"))
    assert_allow(bash_rules_bundle_universal, bash_event("git mv -f src/old.py src/new.py"))
    assert_deny(bash_rules_bundle_universal, bash_event("git mv /tmp/file.txt local.txt"))
    assert_deny(bash_rules_bundle_universal, bash_event("git mv file.txt ../outside.txt"))


def test_git_push_force(bash_event):
    assert_deny(bash_rules_bundle_universal, bash_event("git push --force"))
    assert_deny(bash_rules_bundle_universal, bash_event("git push -f"))
    assert_deny(bash_rules_bundle_universal, bash_event("git push --force origin main"))
    assert_deny(bash_rules_bundle_universal, bash_event("git push -f origin main"))


def test_git_rm(bash_event):
    assert_deny(bash_rules_bundle_universal, bash_event("git rm file.txt"))
    assert_deny(bash_rules_bundle_universal, bash_event("git rm -r directory/"))
    assert_deny(bash_rules_bundle_universal, bash_event("git rm --cached file.txt"))
    assert_deny(bash_rules_bundle_universal, bash_event("git rm -f file.txt"))


def test_git_with_c_option(bash_event):
    assert_allow(bash_rules_bundle_universal, bash_event("git -C /path/to/repo add file.txt"))
    assert_allow(bash_rules_bundle_universal, bash_event('git -C src commit -m "message"'))
    assert_deny(bash_rules_bundle_universal, bash_event("git -C /repo push --force"))
