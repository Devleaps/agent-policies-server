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
        "export PATH=bin",
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
        "export",
    ],
)
def test_export_other_defers_to_user(client, base_event, command):
    check_policy(client, base_event, command, None)


def test_export_then_allowed_command(client, base_event):
    check_policy(client, base_event, "export A=B && pwd", "allow")
