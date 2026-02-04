"""
HTTP Integration Tests for Dangerous Commands
"""

from tests.http.conftest import check_policy


def test_kill_denied(client, base_event):
    check_policy(client, base_event, "kill 1234", "deny")


def test_killall_denied(client, base_event):
    check_policy(client, base_event, "killall python", "deny")


def test_xargs_rm_denied(client, base_event):
    check_policy(client, base_event, "find . -name '*.tmp' | xargs rm", "deny")


def test_perl_denied(client, base_event):
    check_policy(client, base_event, "perl -e 'print \"test\"'", "deny")


def test_sudo_denied(client, base_event):
    check_policy(client, base_event, "sudo apt-get install package", "deny")


def test_rm_rf_denied(client, base_event):
    check_policy(client, base_event, "rm -rf /important/data", "deny")


def test_timeout_kill_denied(client, base_event):
    check_policy(client, base_event, "timeout --kill-after=5s 10s command", "deny")
