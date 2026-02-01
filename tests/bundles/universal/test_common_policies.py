import pytest
from src.evaluation import evaluate_bash_rules
from tests.helpers import assert_allow


def test_rule_functionality(bash_event):
    assert_allow(evaluate_bash_rules, bash_event("pwd"))
    assert_allow(evaluate_bash_rules, bash_event("ps aux"))
    assert_allow(evaluate_bash_rules, bash_event("which python"))
