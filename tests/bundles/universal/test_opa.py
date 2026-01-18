from src.bundles_impl import bash_rules_bundle_universal
from tests.helpers import assert_allow, assert_ask


def test_opa_test(bash_event):
    """Test that opa test command is allowed"""
    assert_allow(bash_rules_bundle_universal, bash_event("opa test"))
    assert_allow(bash_rules_bundle_universal, bash_event("opa test policies/"))
    assert_allow(bash_rules_bundle_universal, bash_event("opa test -v policies/"))
    assert_allow(bash_rules_bundle_universal, bash_event("opa test --verbose policies/"))


def test_opa_other_commands_not_allowed(bash_event):
    """Test that other opa commands default to ASK"""
    assert_ask(bash_rules_bundle_universal, bash_event("opa eval"))
    assert_ask(bash_rules_bundle_universal, bash_event("opa check policies/"))
    assert_ask(bash_rules_bundle_universal, bash_event("opa fmt -w policies/"))
