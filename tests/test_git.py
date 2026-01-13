"""Tests for git command policies."""

import pytest
from src.bundles.universal.git import (
    git_checkout_rule,
    git_fetch_rule,
    git_pull_rule,
    git_branch_delete_force_rule,
)
from tests.helpers import assert_allow, assert_deny, assert_pass


def test_git_checkout_allows_basic_checkout(bash_event):
    """git checkout should be allowed."""
    assert_allow(git_checkout_rule, bash_event("git checkout main"))


def test_git_checkout_allows_with_flags(bash_event):
    """git checkout with flags should be allowed."""
    assert_allow(git_checkout_rule, bash_event("git checkout -b feature-branch"))


def test_git_checkout_allows_with_path(bash_event):
    """git checkout with file path should be allowed."""
    assert_allow(git_checkout_rule, bash_event("git checkout HEAD -- file.txt"))


def test_git_fetch_allows_basic_fetch(bash_event):
    """git fetch should be allowed."""
    assert_allow(git_fetch_rule, bash_event("git fetch"))


def test_git_fetch_allows_with_remote(bash_event):
    """git fetch with remote should be allowed."""
    assert_allow(git_fetch_rule, bash_event("git fetch origin"))


def test_git_fetch_allows_with_flags(bash_event):
    """git fetch with flags should be allowed."""
    assert_allow(git_fetch_rule, bash_event("git fetch --all --prune"))


def test_git_pull_allows_basic_pull(bash_event):
    """git pull should be allowed."""
    assert_allow(git_pull_rule, bash_event("git pull"))


def test_git_pull_allows_with_remote_and_branch(bash_event):
    """git pull with remote and branch should be allowed."""
    assert_allow(git_pull_rule, bash_event("git pull origin main"))


def test_git_pull_allows_with_flags(bash_event):
    """git pull with flags should be allowed."""
    assert_allow(git_pull_rule, bash_event("git pull --rebase"))


def test_git_branch_delete_force_denies(bash_event):
    """git branch -D should be denied."""
    assert_deny(git_branch_delete_force_rule, bash_event("git branch -D feature-branch"))


def test_git_branch_delete_force_denies_with_multiple_branches(bash_event):
    """git branch -D with multiple branches should be denied."""
    assert_deny(git_branch_delete_force_rule, bash_event("git branch -D branch1 branch2"))


def test_git_branch_safe_delete_passes(bash_event):
    """git branch -d (safe delete) should pass through."""
    assert_pass(git_branch_delete_force_rule, bash_event("git branch -d feature-branch"))


def test_git_branch_list_passes(bash_event):
    """git branch without delete should pass through."""
    assert_pass(git_branch_delete_force_rule, bash_event("git branch"))


def test_git_branch_create_passes(bash_event):
    """git branch with branch name should pass through."""
    assert_pass(git_branch_delete_force_rule, bash_event("git branch new-feature"))
