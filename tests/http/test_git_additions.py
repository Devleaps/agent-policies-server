"""
HTTP Integration Tests for new git command rules
"""

from tests.http.conftest import check_policy


def test_git_ls_tree_allowed(client, base_event):
    check_policy(client, base_event, "git ls-tree HEAD", "allow")


def test_git_ls_tree_no_args_allowed(client, base_event):
    check_policy(client, base_event, "git ls-tree", "allow")


def test_git_version_allowed(client, base_event):
    check_policy(client, base_event, "git --version", "allow")
