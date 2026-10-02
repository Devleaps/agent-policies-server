"""
HTTP Integration Tests for uv run with test files: running a test file
directly is denied, but tools may take test files as arguments.
"""

import pytest

from tests.http.conftest import check_policy


@pytest.fixture
def uv_event(base_event):
    base_event["bundles"] = ["universal", "python_uv"]
    return base_event


@pytest.mark.parametrize(
    "command",
    [
        "uv run pytest tests/test_foo.py",
        "uv run pytest tests/test_foo.py::test_bar",
        "uv run black tests/test_foo.py",
        "uv run ruff check tests/test_foo.py src/foo_test.py",
        "uv run mypy tests/test_foo.py",
    ],
)
def test_tools_on_test_files_allowed(client, uv_event, command):
    check_policy(client, uv_event, command, "allow")


@pytest.mark.parametrize(
    "command",
    [
        "uv run tests/test_foo.py",
        "uv run src/foo_test.py",
        "uv run test_foo.py --verbose",
    ],
)
def test_running_test_file_directly_denied(client, uv_event, command):
    data = check_policy(client, uv_event, command, "deny")
    assert "uv run pytest" in data["hookSpecificOutput"]["permissionDecisionReason"]
