"""
HTTP Integration Tests for uvx commands
"""

from tests.http.conftest import check_policy


def test_uvx_black_allowed(client, base_event):
    check_policy(client, base_event, "uvx black .", "allow")


def test_uvx_mypy_allowed(client, base_event):
    check_policy(client, base_event, "uvx mypy src/", "allow")


def test_uvx_bandit_allowed(client, base_event):
    check_policy(client, base_event, "uvx bandit -r src/", "allow")


def test_uvx_ruff_allowed(client, base_event):
    check_policy(client, base_event, "uvx ruff check .", "allow")


def test_uvx_unknown_tool_defers(client, base_event):
    """uvx with non-whitelisted tool defers to user"""
    check_policy(client, base_event, "uvx some-random-tool", None)
