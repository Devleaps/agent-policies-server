"""
HTTP Integration Tests for gh repo clone
"""

from tests.http.conftest import check_policy


def test_gh_repo_clone_allowed(client, base_event):
    check_policy(client, base_event, "gh repo clone user/repo", "allow")


def test_gh_repo_clone_with_directory_allowed(client, base_event):
    check_policy(client, base_event, "gh repo clone user/repo my-dir", "allow")
