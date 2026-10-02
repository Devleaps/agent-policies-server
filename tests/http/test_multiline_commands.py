"""
HTTP Integration Tests: every line of a multi-line command is evaluated,
not just the first.
"""

import pytest

from src.evaluation.parser import BashCommandParser
from tests.http.conftest import check_policy


@pytest.mark.parametrize(
    "command",
    [
        "pwd\nrm -rf build",
        "git status && pwd\nls; sudo ls",
        "echo ok\n\nkill 1234",
    ],
)
def test_deny_on_a_later_line_denies(client, base_event, command):
    check_policy(client, base_event, command, "deny")


def test_all_lines_allowed_is_allowed(client, base_event):
    check_policy(client, base_event, "pwd\nls\ngit status", "allow")


def test_every_line_is_parsed_in_order():
    parsed = BashCommandParser.parse("echo ok\nbash evil.sh && ls\npwd")
    executables = [parsed.executable] + [c.executable for c in parsed.chained]
    assert executables == ["echo", "bash", "ls", "pwd"]


@pytest.mark.parametrize(
    "command",
    [
        'ls | while read d; do rm "$d"; done',
        "ls; for x in a; do sudo rm x; done",
        "pwd && (bash evil.sh)",
    ],
)
def test_compound_parts_are_not_dropped(client, base_event, command):
    """A loop or subshell inside a list or pipeline used to be skipped, so
    only the simple commands around it were evaluated and allowed."""
    check_policy(client, base_event, command, None)


@pytest.mark.parametrize(
    "command",
    ["X=$(bash evil.sh) ls", "X=`bash evil.sh` pwd"],
)
def test_substitution_in_prefix_assignment_is_not_ignored(client, base_event, command):
    check_policy(client, base_event, command, None)


def test_plain_prefix_assignment_unchanged(client, base_event):
    check_policy(client, base_event, "FOO=1 ls", "allow")
