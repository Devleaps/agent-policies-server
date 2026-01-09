import pytest
from src.universal.absolute_path_executables import absolute_path_executable_rule
from src.universal.rm_allow import rm_safe_operations_rule
from src.universal.tmp_cat_block import tmp_cat_block_rule
from src.universal.whitelist_safe_paths import whitelist_safe_paths_rule
from tests.helpers import assert_allow, assert_deny, assert_deny_count, assert_pass


def test_absolute_path_executables(bash_event):
    assert_deny(absolute_path_executable_rule, bash_event("/usr/bin/python script.py"))
    assert_deny(absolute_path_executable_rule, bash_event(".venv/bin/pytest tests/"))
    assert_deny(absolute_path_executable_rule, bash_event("/Users/username/project/.venv/bin/pytest tests/"))
    assert_pass(absolute_path_executable_rule, bash_event("pytest tests/"))
    assert_pass(absolute_path_executable_rule, bash_event("./script.sh arg1 arg2"))


def test_rm(bash_event):
    assert_deny(rm_safe_operations_rule, bash_event("rm -rf directory/"), "trash")
    assert_deny(rm_safe_operations_rule, bash_event("rm file.txt"), "trash")
    assert_deny_count(rm_safe_operations_rule, bash_event("rm /tmp/file.txt"), 2)
    assert_deny_count(rm_safe_operations_rule, bash_event("rm -rf /"), 2)


def test_trash(bash_event):
    assert_deny(whitelist_safe_paths_rule, bash_event("trash /etc/hosts"), "absolute paths are not allowed")
    assert_deny(whitelist_safe_paths_rule, bash_event("trash /"), "absolute paths are not allowed")
    assert_deny(whitelist_safe_paths_rule, bash_event("trash /tmp/file.txt"), "absolute paths are not allowed")
    assert_deny(whitelist_safe_paths_rule, bash_event("trash ~/Documents/file.txt"), "tilde-based paths (~) are not allowed")
    assert_deny(whitelist_safe_paths_rule, bash_event("trash ../file.txt"), "upward directory traversal")
    assert_deny(whitelist_safe_paths_rule, bash_event("trash foo/../bar/file.txt"), "upward directory traversal")
    assert_allow(whitelist_safe_paths_rule, bash_event("trash file.txt"))
    assert_allow(whitelist_safe_paths_rule, bash_event("trash src/components/Button.tsx"))
    assert_allow(whitelist_safe_paths_rule, bash_event("trash file1.txt file2.txt"))
    assert_allow(whitelist_safe_paths_rule, bash_event("trash *.log"))
    assert_allow(whitelist_safe_paths_rule, bash_event("trash -v file.txt"))


def test_touch(bash_event):
    assert_allow(whitelist_safe_paths_rule, bash_event("touch newfile.txt"))
    assert_allow(whitelist_safe_paths_rule, bash_event("touch -t 202301011200 file.txt"))
    assert_deny(whitelist_safe_paths_rule, bash_event("touch /tmp/file.txt"))
    assert_deny(whitelist_safe_paths_rule, bash_event("touch ../file.txt"))


def test_tmp_cat_block(bash_event):
    assert_deny(tmp_cat_block_rule, bash_event("cat > /tmp/file.txt << EOF"))
    assert_deny(tmp_cat_block_rule, bash_event("cat >> /tmp/output.log << EOF"))
    assert_pass(tmp_cat_block_rule, bash_event("cat > output.txt << EOF"))
