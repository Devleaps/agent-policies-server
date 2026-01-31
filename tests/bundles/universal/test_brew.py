from src.bundles_impl import evaluate_bash_rules
from tests.helpers import assert_allow


def test_brew_info(bash_event):
    """Test that brew info is allowed"""
    assert_allow(evaluate_bash_rules, bash_event("brew info python"))
    assert_allow(evaluate_bash_rules, bash_event("brew info --json python"))
    assert_allow(evaluate_bash_rules, bash_event("brew info node@18"))


def test_brew_uses(bash_event):
    """Test that brew uses is allowed"""
    assert_allow(evaluate_bash_rules, bash_event("brew uses python"))
    assert_allow(evaluate_bash_rules, bash_event("brew uses --installed openssl"))
    assert_allow(evaluate_bash_rules, bash_event("brew uses --recursive node"))


def test_brew_cat(bash_event):
    """Test that brew cat is allowed"""
    assert_allow(evaluate_bash_rules, bash_event("brew cat python"))
    assert_allow(evaluate_bash_rules, bash_event("brew cat node"))
    assert_allow(evaluate_bash_rules, bash_event("brew cat postgresql"))
