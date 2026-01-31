"""Quick test to check redirect policies."""
from src.bundles_impl import evaluate_bash_rules
from tests.helpers import assert_allow, assert_deny
import pytest


def test_absolute_path_redirects(bash_event):
    """Test various absolute path redirects."""
    # /dev/null - common and safe, should be allowed
    assert_allow(evaluate_bash_rules, bash_event("echo test 2>/dev/null"))

    # /etc/passwd - should be blocked
    assert_deny(evaluate_bash_rules, bash_event("echo test > /etc/passwd"))

    # /home/user/file - should be blocked
    assert_deny(evaluate_bash_rules, bash_event("echo test > /home/user/file.txt"))

    # /tmp/ - should be blocked
    assert_deny(evaluate_bash_rules, bash_event("echo test > /tmp/file.txt"))
