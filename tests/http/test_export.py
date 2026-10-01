"""
HTTP Integration Tests for export.
"""

import pytest

from tests.http.conftest import check_policy


@pytest.mark.parametrize(
    "command",
    [
        "export A=B",
        "export NODE_ENV=production",
        "export A=B C=D",
        "export GREETING='hello world'",
        'export GREETING="hello world"',
        "export EMPTY=",
        "export A=$B",
        'export A="${HOME}/x"',
    ],
)
def test_export_assignment_allowed(client, base_event, command):
    check_policy(client, base_event, command, "allow")


@pytest.mark.parametrize(
    "command",
    [
        "export A",
        "export -n A",
        # Variables that change which program runs or what it loads
        "export PATH=bin",
        "export PATH=.:$PATH",
        "export PYTHONPATH=src",
        "export LD_PRELOAD=evil.so",
        "export DYLD_INSERT_LIBRARIES=evil.dylib",
        "export GIT_SSH_COMMAND=evil",
        "export PAGER=evil",
        "export BASH_ENV=evil.sh",
        "export GIT_CONFIG_COUNT=1",
        "export A=B PATH=bin",
        "export",
    ],
)
def test_export_other_defers_to_user(client, base_event, command):
    check_policy(client, base_event, command, None)


def test_export_then_allowed_command(client, base_event):
    check_policy(client, base_event, "export A=B && pwd", "allow")


def test_export_path_then_command_defers_to_user(client, base_event):
    """A ./git could run instead of git once . is on PATH."""
    check_policy(client, base_event, "export PATH=.:$PATH && git status", None)
