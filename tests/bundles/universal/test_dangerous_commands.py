"""Test dangerous command combinations."""
from src.bundles_impl import bash_rules_bundle_universal
from tests.helpers import assert_deny


def test_kill_command_blocked(bash_event):
    assert_deny(bash_rules_bundle_universal, bash_event("kill 1234"))
    assert_deny(bash_rules_bundle_universal, bash_event("kill -9 5678"))


def test_xargs_blocked(bash_event):
    assert_deny(bash_rules_bundle_universal, bash_event("xargs rm"))
    assert_deny(bash_rules_bundle_universal, bash_event("xargs kill -9"))
    assert_deny(bash_rules_bundle_universal, bash_event("xargs rm -rf"))
