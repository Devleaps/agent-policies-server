"""Quick test to check redirect policies."""
from src.bundles.universal import bash_rules_bundle_universal
from tests.helpers import assert_allow, assert_deny
import pytest


def test_absolute_path_redirects(bash_event):
    """Test various absolute path redirects."""
    # /dev/null - common and safe, should be allowed
    assert_allow(bash_rules_bundle_universal, bash_event("echo test 2>/dev/null"))

    # /etc/passwd - should be blocked
    assert_deny(bash_rules_bundle_universal, bash_event("echo test > /etc/passwd"))

    # /home/user/file - should be blocked
    assert_deny(bash_rules_bundle_universal, bash_event("echo test > /home/user/file.txt"))

    # /tmp/ - should be blocked
    assert_deny(bash_rules_bundle_universal, bash_event("echo test > /tmp/file.txt"))
