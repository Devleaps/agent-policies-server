"""
HTTP Integration Tests for regal (Rego linter) and installing it via brew.
"""

from tests.http.conftest import check_policy


def test_brew_install_regal_allowed(client, base_event):
    check_policy(client, base_event, "brew install regal", "allow")


def test_brew_install_other_formula_defers_to_user(client, base_event):
    check_policy(client, base_event, "brew install wget", None)


def test_brew_install_regal_with_extra_formula_defers_to_user(client, base_event):
    check_policy(client, base_event, "brew install regal wget", None)


def test_regal_lint_allowed(client, base_event):
    check_policy(client, base_event, "regal lint policies", "allow")


def test_regal_lint_no_path_allowed(client, base_event):
    check_policy(client, base_event, "regal lint", "allow")


def test_regal_lint_with_format_allowed(client, base_event):
    check_policy(client, base_event, "regal lint --format pretty policies/", "allow")


def test_regal_lint_unsafe_path_denied(client, base_event):
    check_policy(client, base_event, "regal lint /etc", "deny")


def test_regal_fix_defers_to_user(client, base_event):
    check_policy(client, base_event, "regal fix policies", None)
