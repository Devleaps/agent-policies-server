"""
HTTP Integration Tests: source is allowed for a virtualenv activate script.
"""

import pytest

from tests.http.conftest import check_policy


@pytest.mark.parametrize(
    "command",
    [
        "source venv/bin/activate",
        "source .venv/bin/activate",
        "source ./.venv/bin/activate",
        "source .venv/bin/activate && pytest",
    ],
)
def test_source_activate_allowed(client, base_event, command):
    check_policy(client, base_event, command, "allow")


@pytest.mark.parametrize(
    "command",
    [
        # The activate path elsewhere in the command does not count
        "source arbitrary && echo venv/bin/activate",
        "source evil.sh venv/bin/activate",
        "source /tmp/venv/bin/activate",
        "source ../other/.venv/bin/activate",
        "source evil.sh",
    ],
)
def test_source_other_defers_to_user(client, base_event, command):
    check_policy(client, base_event, command, None)
