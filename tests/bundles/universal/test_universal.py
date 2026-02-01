import pytest
from src.evaluation import evaluate_bash_rules
from tests.helpers import assert_allow, assert_ask, assert_deny, assert_deny_count, assert_pass


def test_absolute_path_executables(bash_event):
    assert_deny(evaluate_bash_rules, bash_event("/usr/bin/python script.py"))
    assert_deny(evaluate_bash_rules, bash_event(".venv/bin/pytest tests/"))
    assert_deny(evaluate_bash_rules, bash_event("/Users/username/project/.venv/bin/pytest tests/"))
    assert_allow(evaluate_bash_rules, bash_event("pytest tests/"))
    assert_ask(evaluate_bash_rules, bash_event("./script.sh arg1 arg2"))


def test_rm(bash_event):
    assert_deny(evaluate_bash_rules, bash_event("rm -rf directory/"))
    assert_deny(evaluate_bash_rules, bash_event("rm file.txt"))
    assert_deny(evaluate_bash_rules, bash_event("rm /tmp/file.txt"))
    assert_deny(evaluate_bash_rules, bash_event("rm -rf /"))


def test_trash(bash_event):
    assert_deny(evaluate_bash_rules, bash_event("trash /etc/hosts"))
    assert_deny(evaluate_bash_rules, bash_event("trash /"))
    assert_deny(evaluate_bash_rules, bash_event("trash /tmp/file.txt"))
    assert_deny(evaluate_bash_rules, bash_event("trash ~/Documents/file.txt"))
    assert_deny(evaluate_bash_rules, bash_event("trash ../file.txt"))
    assert_deny(evaluate_bash_rules, bash_event("trash foo/../bar/file.txt"))
    assert_allow(evaluate_bash_rules, bash_event("trash file.txt"))
    assert_allow(evaluate_bash_rules, bash_event("trash src/components/Button.tsx"))
    assert_allow(evaluate_bash_rules, bash_event("trash file1.txt file2.txt"))
    assert_allow(evaluate_bash_rules, bash_event("trash *.log"))
    assert_allow(evaluate_bash_rules, bash_event("trash -v file.txt"))


def test_touch(bash_event):
    assert_allow(evaluate_bash_rules, bash_event("touch newfile.txt"))
    assert_allow(evaluate_bash_rules, bash_event("touch -t 202301011200 file.txt"))
    assert_deny(evaluate_bash_rules, bash_event("touch /tmp/file.txt"))
    assert_deny(evaluate_bash_rules, bash_event("touch ../file.txt"))


def test_tmp_redirect_deny(bash_event):
    assert_deny(evaluate_bash_rules, bash_event("echo 'test' > /tmp/file.txt"))
    assert_deny(evaluate_bash_rules, bash_event("ls > /tmp/output.log"))
    assert_deny(evaluate_bash_rules, bash_event("cat file.txt > /tmp/output.txt"))
    assert_allow(evaluate_bash_rules, bash_event("echo 'test' > file.txt"))
    assert_allow(evaluate_bash_rules, bash_event("cat > output.txt"))


def test_test_command(bash_event):
    assert_allow(evaluate_bash_rules, bash_event("test -f file.txt"))
    assert_allow(evaluate_bash_rules, bash_event("test -d src/components"))
    assert_allow(evaluate_bash_rules, bash_event("test -e README.md"))
    assert_allow(evaluate_bash_rules, bash_event("test -r scripts/build.sh"))
    assert_allow(evaluate_bash_rules, bash_event("test -w output.log"))
    assert_allow(evaluate_bash_rules, bash_event("test -x run.sh"))
    assert_allow(evaluate_bash_rules, bash_event("test -s data.json"))
    assert_deny(evaluate_bash_rules, bash_event("test -f /etc/passwd"))
    assert_deny(evaluate_bash_rules, bash_event("test -d /tmp"))
    assert_deny(evaluate_bash_rules, bash_event("test -e ../config.json"))


def test_bracket_command(bash_event):
    assert_allow(evaluate_bash_rules, bash_event("[ -f file.txt ]"))
    assert_allow(evaluate_bash_rules, bash_event("[ -d src ]"))
    assert_allow(evaluate_bash_rules, bash_event("[ -e README.md ]"))
    assert_deny(evaluate_bash_rules, bash_event("[ -f /etc/passwd ]"))
    assert_deny(evaluate_bash_rules, bash_event("[ -d /tmp ]"))
