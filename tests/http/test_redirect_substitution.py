"""
HTTP Integration Tests: command substitution in a heredoc body or here-string
runs, so it must not be ignored.
"""

import pytest

from tests.http.conftest import check_policy


@pytest.mark.parametrize(
    "command",
    [
        "cat << EOF\n$(rm -rf build)\nEOF",
        "cat << EOF\n`rm -rf build`\nEOF",
        "cat << EOF > out.txt\n`rm -rf build`\nEOF",
        'cat <<< "$(rm -rf build)"',
        "cat <<< $(rm -rf build)",
    ],
)
def test_substitution_in_redirect_defers_to_user(client, base_event, command):
    check_policy(client, base_event, command, None)


def test_plain_heredoc_still_allowed(client, base_event):
    check_policy(client, base_event, "cat << EOF\nplain text\nEOF", "allow")


def test_quoted_here_string_is_not_a_quoted_heredoc(client, base_event):
    check_policy(client, base_event, 'grep x <<< "some text"', "allow")


@pytest.mark.parametrize("command", ["cat << 'EOF'\nx\nEOF", 'cat <<-"EOF"\nx\nEOF'])
def test_quoted_heredoc_still_denied(client, base_event, command):
    check_policy(client, base_event, command, "deny")


def test_file_redirect_after_heredoc_is_checked(client, base_event):
    check_policy(client, base_event, "cat << EOF > /etc/profile\ntext\nEOF", "deny")
