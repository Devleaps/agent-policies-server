"""
HTTP Integration Tests for Homebrew Commands
"""

from tests.http.conftest import check_policy


def test_brew_info_allowed(client, base_event):
    check_policy(client, base_event, "brew info python", "allow")


def test_brew_uses_allowed(client, base_event):
    check_policy(client, base_event, "brew uses --installed python", "allow")


def test_brew_cat_allowed(client, base_event):
    check_policy(client, base_event, "brew cat python", "allow")
