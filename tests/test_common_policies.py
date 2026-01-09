import pytest
from src.universal import whitelist_always_rule
from tests.helpers import assert_allow


def test_rule_functionality(bash_event):
    assert_allow(whitelist_always_rule, bash_event("pwd"))
    assert_allow(whitelist_always_rule, bash_event("ps aux"))
    assert_allow(whitelist_always_rule, bash_event("which python"))
