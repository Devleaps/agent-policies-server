"""
HTTP Integration Tests: test / [ only treat file-test operands as paths,
so string tests on variables are allowed and file tests stay guarded.
"""

import pytest

from tests.http.conftest import check_policy


@pytest.mark.parametrize(
    "command",
    [
        '[ -n "$X" ]',
        'test -z "$X"',
        '[ "$a" = "b" ]',
        '[ "$count" -eq 3 ]',
        "[ -f a.txt ]",
        "test -d src",
        "[ a.txt -nt b.txt ]",
        "[ -f a.txt -a -f b.txt ]",
        "[ -n x -a -n y ]",
        '[ -n "$X" ] && echo set',
    ],
)
def test_string_tests_and_safe_file_tests_allowed(client, base_event, command):
    check_policy(client, base_event, command, "allow")


@pytest.mark.parametrize(
    "command",
    [
        "[ -f /etc/passwd ]",
        '[ -f "$HOME/.ssh/id_rsa" ]',
        "test -e ../secret",
        "[ a.txt -nt /etc/passwd ]",
        "[ /etc/passwd -nt a.txt ]",
        # -a is "file exists" where an expression starts
        "test -a /etc/passwd",
        "[ -a /etc/passwd ]",
        "[ ! -a /etc/passwd ]",
        # Every file test counts, not only the last of each operator
        "[ -f /etc/passwd -o -f README.md ]",
        "[ -f a.txt -a -f /etc/passwd ]",
    ],
)
def test_unsafe_file_operands_denied(client, base_event, command):
    check_policy(client, base_event, command, "deny")
