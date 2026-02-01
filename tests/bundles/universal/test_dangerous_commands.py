"""Test dangerous command combinations."""
from src.evaluation import evaluate_bash_rules
from tests.helpers import assert_deny


def test_kill_command_blocked(bash_event):
    assert_deny(evaluate_bash_rules, bash_event("kill 1234"))
    assert_deny(evaluate_bash_rules, bash_event("kill -9 5678"))


def test_xargs_blocked(bash_event):
    assert_deny(evaluate_bash_rules, bash_event("xargs rm"))
    assert_deny(evaluate_bash_rules, bash_event("xargs kill -9"))
    assert_deny(evaluate_bash_rules, bash_event("xargs rm -rf"))
