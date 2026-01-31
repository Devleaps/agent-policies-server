from src.bundles_impl import evaluate_bash_rules
from tests.helpers import assert_allow, assert_ask


def test_opa_test(bash_event):
    """Test that opa test command is allowed"""
    assert_allow(evaluate_bash_rules, bash_event("opa test"))
    assert_allow(evaluate_bash_rules, bash_event("opa test policies/"))
    assert_allow(evaluate_bash_rules, bash_event("opa test -v policies/"))
    assert_allow(evaluate_bash_rules, bash_event("opa test --verbose policies/"))


def test_opa_other_commands_not_allowed(bash_event):
    """Test that other opa commands default to ASK"""
    assert_ask(evaluate_bash_rules, bash_event("opa eval"))
    assert_ask(evaluate_bash_rules, bash_event("opa check policies/"))
    assert_ask(evaluate_bash_rules, bash_event("opa fmt -w policies/"))
