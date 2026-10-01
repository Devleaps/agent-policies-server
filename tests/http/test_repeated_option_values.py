"""
HTTP Integration Tests: an option given twice must not hide its first value.

The parser keeps options in a dict, so the second -n used to overwrite the
first and the path after it was never checked.
"""

import pytest

from src.evaluation.parser import BashCommandParser
from tests.http.conftest import check_policy


@pytest.mark.parametrize(
    "command",
    [
        "cat -n ~/.ssh/id_rsa -n README.md",
        "cat -n /etc/passwd -n README.md",
        "cat --number=/etc/passwd --number=README.md",
        "head -n /etc/passwd -n 5 README.md",
    ],
)
def test_first_value_of_a_repeated_option_is_checked(client, base_event, command):
    check_policy(client, base_event, command, "deny")


def test_repeated_option_keeps_last_value_and_earlier_ones_separately():
    parsed = BashCommandParser.parse("grep -e x -e y README.md")
    assert parsed.options == {"-e": "y"}
    assert parsed.repeated_options == {"-e": ["x"]}
    assert parsed.arguments == ["README.md"]


def test_repeated_safe_option_values_still_allowed(client, base_event):
    check_policy(client, base_event, "grep -e x -e y README.md", "allow")


def test_repeated_option_value_does_not_look_like_a_positional(client, base_event):
    """An earlier --query value must not pass for the az action."""
    check_policy(
        client,
        base_event,
        "az group delete --name demo --query list --query name --yes",
        "deny",
    )


def test_every_git_dash_c_path_is_checked(client, base_event):
    check_policy(client, base_event, "git -C /tmp/other-repo -C . status", "deny")
