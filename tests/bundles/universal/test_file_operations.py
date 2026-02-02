"""Tests for file operation commands: ls, grep, du, mkdir, file, tree, df."""

import pytest
from src.evaluation import evaluate_bash_rules
from tests.helpers import assert_allow, assert_deny


# --- ls tests ---

def test_ls_safe_paths(bash_event):
    """Test ls with safe relative paths."""
    assert_allow(evaluate_bash_rules, bash_event("ls"))
    assert_allow(evaluate_bash_rules, bash_event("ls -la"))
    assert_allow(evaluate_bash_rules, bash_event("ls src"))
    assert_allow(evaluate_bash_rules, bash_event("ls -la src/"))


def test_ls_unsafe_paths(bash_event):
    """Test ls with unsafe paths."""
    assert_deny(evaluate_bash_rules, bash_event("ls /tmp"))
    assert_deny(evaluate_bash_rules, bash_event("ls -la /Users/philipp/DevLeaps/*.*"))
    assert_deny(evaluate_bash_rules, bash_event("ls -la /Users/philipp/DevLeaps/*.* 2>/dev/null"))
    assert_deny(evaluate_bash_rules, bash_event("ls ../.."))


# --- grep tests ---

def test_grep_safe_paths(bash_event):
    """Test grep with safe relative paths."""
    assert_allow(evaluate_bash_rules, bash_event('grep "test" file.txt'))
    assert_allow(evaluate_bash_rules, bash_event('grep -n "guidance_activations" policies/demo_flags/*.rego'))
    assert_allow(evaluate_bash_rules, bash_event('grep -r "pattern" src/'))


def test_grep_unsafe_paths(bash_event):
    """Test grep with unsafe paths."""
    assert_deny(evaluate_bash_rules, bash_event('grep -n "test" /Users/philipp/file.txt'))
    assert_deny(evaluate_bash_rules, bash_event('grep "pattern" /tmp/file.txt'))
    assert_deny(evaluate_bash_rules, bash_event('grep -r "text" ../parent/'))


def test_grep_piped(bash_event):
    """Test grep with piped input (no file arguments)."""
    assert_allow(evaluate_bash_rules, bash_event('echo "test" | grep "test"'))
    assert_allow(evaluate_bash_rules, bash_event('cat file.txt | grep "pattern"'))


# --- du tests ---

def test_du_safe_paths(bash_event):
    """Test du with safe relative paths."""
    assert_allow(evaluate_bash_rules, bash_event("du"))
    assert_allow(evaluate_bash_rules, bash_event("du -h"))
    assert_allow(evaluate_bash_rules, bash_event("du src"))
    assert_allow(evaluate_bash_rules, bash_event("du -sh src"))


def test_du_unsafe_paths(bash_event):
    """Test du with unsafe paths."""
    assert_deny(evaluate_bash_rules, bash_event("du /tmp"))
    assert_deny(evaluate_bash_rules, bash_event("du /tmp/somedir"))
    assert_deny(evaluate_bash_rules, bash_event("du ../.."))


# --- mkdir tests ---

def test_mkdir_safe_paths(bash_event):
    """Test mkdir with safe relative paths."""
    assert_allow(evaluate_bash_rules, bash_event("mkdir newdir"))
    assert_allow(evaluate_bash_rules, bash_event("mkdir -p src/subdir"))
    assert_allow(evaluate_bash_rules, bash_event("mkdir dir1 dir2"))


def test_mkdir_unsafe_paths(bash_event):
    """Test mkdir with unsafe paths."""
    assert_deny(evaluate_bash_rules, bash_event("mkdir /tmp/newdir"))
    assert_deny(evaluate_bash_rules, bash_event("mkdir /absolute/path"))
    assert_deny(evaluate_bash_rules, bash_event("mkdir ../outside"))


# --- file tests ---

def test_file_safe_paths(bash_event):
    """Test file command with safe relative paths."""
    assert_allow(evaluate_bash_rules, bash_event("file setup.sh"))
    assert_allow(evaluate_bash_rules, bash_event("file src/*.py"))
    assert_allow(evaluate_bash_rules, bash_event("file skills/*"))


def test_file_unsafe_paths(bash_event):
    """Test file command with unsafe paths."""
    assert_deny(evaluate_bash_rules, bash_event("file /tmp/test"))
    assert_deny(evaluate_bash_rules, bash_event("file /Users/philipp/DevLeaps/agent-skills/skills/*"))
    assert_deny(evaluate_bash_rules, bash_event("file ../outside/file"))


# --- tree tests ---

def test_tree_command(bash_event):
    """Test tree command (always allowed, read-only)."""
    assert_allow(evaluate_bash_rules, bash_event("tree"))
    assert_allow(evaluate_bash_rules, bash_event("tree -L 2"))
    assert_allow(evaluate_bash_rules, bash_event("tree -L 2 -I '__pycache__'"))
    assert_allow(evaluate_bash_rules, bash_event("tree src"))
    assert_allow(evaluate_bash_rules, bash_event("tree -a"))


# --- df tests ---

def test_df_command(bash_event):
    """Test df command (always allowed, system info)."""
    assert_allow(evaluate_bash_rules, bash_event("df"))
    assert_allow(evaluate_bash_rules, bash_event("df -h"))
    assert_allow(evaluate_bash_rules, bash_event("df -h /"))
    assert_allow(evaluate_bash_rules, bash_event("df --human-readable"))
