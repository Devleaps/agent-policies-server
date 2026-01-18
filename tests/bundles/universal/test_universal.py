import pytest
from src.bundles_impl import bash_rules_bundle_universal
from tests.helpers import assert_allow, assert_ask, assert_deny, assert_deny_count, assert_pass


def test_absolute_path_executables(bash_event):
    assert_deny(bash_rules_bundle_universal, bash_event("/usr/bin/python script.py"))
    assert_deny(bash_rules_bundle_universal, bash_event(".venv/bin/pytest tests/"))
    assert_deny(bash_rules_bundle_universal, bash_event("/Users/username/project/.venv/bin/pytest tests/"))
    assert_allow(bash_rules_bundle_universal, bash_event("pytest tests/"))
    assert_ask(bash_rules_bundle_universal, bash_event("./script.sh arg1 arg2"))


def test_rm(bash_event):
    assert_deny(bash_rules_bundle_universal, bash_event("rm -rf directory/"))
    assert_deny(bash_rules_bundle_universal, bash_event("rm file.txt"))
    assert_deny(bash_rules_bundle_universal, bash_event("rm /tmp/file.txt"))
    assert_deny(bash_rules_bundle_universal, bash_event("rm -rf /"))


def test_trash(bash_event):
    assert_deny(bash_rules_bundle_universal, bash_event("trash /etc/hosts"))
    assert_deny(bash_rules_bundle_universal, bash_event("trash /"))
    assert_deny(bash_rules_bundle_universal, bash_event("trash /tmp/file.txt"))
    assert_deny(bash_rules_bundle_universal, bash_event("trash ~/Documents/file.txt"))
    assert_deny(bash_rules_bundle_universal, bash_event("trash ../file.txt"))
    assert_deny(bash_rules_bundle_universal, bash_event("trash foo/../bar/file.txt"))
    assert_allow(bash_rules_bundle_universal, bash_event("trash file.txt"))
    assert_allow(bash_rules_bundle_universal, bash_event("trash src/components/Button.tsx"))
    assert_allow(bash_rules_bundle_universal, bash_event("trash file1.txt file2.txt"))
    assert_allow(bash_rules_bundle_universal, bash_event("trash *.log"))
    assert_allow(bash_rules_bundle_universal, bash_event("trash -v file.txt"))


def test_touch(bash_event):
    assert_allow(bash_rules_bundle_universal, bash_event("touch newfile.txt"))
    assert_allow(bash_rules_bundle_universal, bash_event("touch -t 202301011200 file.txt"))
    assert_deny(bash_rules_bundle_universal, bash_event("touch /tmp/file.txt"))
    assert_deny(bash_rules_bundle_universal, bash_event("touch ../file.txt"))


def test_tmp_redirect_deny(bash_event):
    assert_deny(bash_rules_bundle_universal, bash_event("echo 'test' > /tmp/file.txt"))
    assert_deny(bash_rules_bundle_universal, bash_event("ls > /tmp/output.log"))
    assert_deny(bash_rules_bundle_universal, bash_event("cat file.txt > /tmp/output.txt"))
    assert_allow(bash_rules_bundle_universal, bash_event("echo 'test' > file.txt"))
    assert_allow(bash_rules_bundle_universal, bash_event("cat > output.txt"))
