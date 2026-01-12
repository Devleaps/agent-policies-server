"""Test bash evaluator behavior with piped/chained commands."""
from src.core import evaluate_bash_rules, command
from src.bundles.universal.universal import kill_block_rule, lsof_rule


def test_piped_command_with_unmatched_middle_command(bash_event):
    """Bundle matched lsof but not xargs, should yield ASK for xargs."""
    rules = [lsof_rule, kill_block_rule]
    event = bash_event("lsof -ti :8338 | xargs kill -9")

    results = list(evaluate_bash_rules(event, rules))

    actions = [r.action for r in results]
    assert "allow" in actions, "Should allow lsof"
    assert "ask" in actions, "Should ask about xargs (had match, but xargs unmatched)"


def test_single_command_no_match_yields_ask(bash_event):
    """Bundle matched nothing, yields ASK."""
    rules = [kill_block_rule]
    event = bash_event("xargs something")
    results = list(evaluate_bash_rules(event, rules))
    assert len(results) == 1
    assert results[0].action == "ask"


def test_chained_command_with_partial_match(bash_event):
    """Bundle matched kill but not echo, should yield DENY + ASK."""
    rules = [kill_block_rule]
    event = bash_event("echo hello && kill -9 1234")
    results = list(evaluate_bash_rules(event, rules))

    actions = [r.action for r in results]
    assert "deny" in actions, "Should deny kill"
    assert "ask" in actions, "Should ask about echo (had match, but echo unmatched)"
