import pytest
from src.bundles_impl import bash_rules_bundle_universal
from tests.helpers import assert_allow


def test_rule_functionality(bash_event):
    assert_allow(bash_rules_bundle_universal, bash_event("pwd"))
    assert_allow(bash_rules_bundle_universal, bash_event("ps aux"))
    assert_allow(bash_rules_bundle_universal, bash_event("which python"))
