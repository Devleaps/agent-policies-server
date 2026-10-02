"""
HTTP Integration Tests: a command chain is only allowed when every
segment is allowed. An allowed segment must not approve a segment that
no rule matches.
"""

import pytest

from tests.http.conftest import check_policy


@pytest.mark.parametrize(
    "command",
    [
        "pwd && bash evil.sh",
        "echo hi; osascript -e 'x'",
        "ls || some-unknown-cmd",
        "cat README.md | some-unknown-filter",
        "some-unknown-cmd && pwd",
        "git status && npx some-package",
        "diff <(some-unknown-cmd) README.md",
        "cat < <(some-unknown-cmd)",
    ],
)
def test_allowed_plus_undecided_defers_to_user(client, base_event, command):
    check_policy(client, base_event, command, None)


@pytest.mark.parametrize(
    "command",
    [
        "pwd && ls",
        "git status; git diff",
        "cat README.md | grep foo | head -n 5",
        "diff <(cat a.txt) b.txt",
        "cat < <(ls)",
    ],
)
def test_all_segments_allowed_is_allowed(client, base_event, command):
    check_policy(client, base_event, command, "allow")


@pytest.mark.parametrize(
    "command",
    [
        "some-unknown-cmd && sudo ls",
        "pwd && rm -rf build",
        "some-unknown-cmd | xargs ls",
        # A process substitution used as a redirect target runs too
        "cat < <(sudo ls)",
        "ls > >(rm -rf build)",
        # Every segment of a longer chain counts, not just the ends
        "pwd && sudo ls && cat README.md",
        "pwd && ls || sudo ls && cat README.md",
    ],
)
def test_deny_in_any_segment_still_denies(client, base_event, command):
    check_policy(client, base_event, command, "deny")


@pytest.mark.parametrize(
    "command",
    [
        'for f in a b; do echo "$f"; done',
        'until [ "$(gh run list --limit 1)" = "completed" ]; do sleep 5; done',
        "while true; do pwd; done",
        "if true; then pwd; fi",
    ],
)
def test_compound_commands_defer_to_user(client, base_event, command):
    """Loops and conditionals stay with the user's own settings until the
    parser can evaluate their inner commands."""
    check_policy(client, base_event, command, None)
