"""Test curl commands with flags like -s that take URL as option value."""
from src.bundles_impl import bash_rules_bundle_universal
from tests.helpers import assert_allow, assert_deny


def test_curl_silent_flag_localhost(bash_event):
    """curl -s with localhost URL should be allowed."""
    assert_allow(bash_rules_bundle_universal, bash_event("curl -s http://localhost:8338/health"))
    assert_allow(bash_rules_bundle_universal, bash_event("curl -s http://127.0.0.1:8338/health"))
    assert_allow(bash_rules_bundle_universal, bash_event("curl -s http://[::1]:8000"))


def test_curl_silent_flag_external(bash_event):
    """curl -s with external URL should be denied."""
    assert_deny(bash_rules_bundle_universal, bash_event("curl -s https://google.com"))
    assert_deny(bash_rules_bundle_universal, bash_event("curl -s https://example.com"))


def test_curl_silent_flag_allowed_domain(bash_event):
    """curl -s with allowed domain should be allowed."""
    assert_allow(bash_rules_bundle_universal, bash_event("curl -s https://agent-policies.devleaps.nl"))
