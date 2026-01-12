"""Helper functions for evaluating rules and asserting results."""

from src.core.command_parser import BashCommandParser, ParseError


def eval_rule(rule_func, event):
    """Evaluate a bundle or rule function with an event and return decisions only.

    Usage:
        results = eval_rule(bash_rules_bundle_universal, bash_event("kill 1234"))
    """
    try:
        results = list(rule_func(event))
    except TypeError:
        if hasattr(event, 'tool_is_bash') and event.tool_is_bash:
            try:
                parsed = BashCommandParser.parse(event.command)
            except ParseError:
                parsed = None
            results = list(rule_func(event, parsed))
        else:
            results = list(rule_func(event))
    return [r for r in results if hasattr(r, 'action')]


def assert_allow(rule_func, event):
    """Assert that ONLY allows were yielded.

    Usage:
        assert_allow(bash_rules_bundle_universal, bash_event("git add file.txt"))
    """
    results = eval_rule(rule_func, event)
    assert len(results) >= 1, f"Expected at least 1 decision, got {len(results)}"

    actions = [r.action for r in results]
    assert all(action == "allow" for action in actions), f"Expected only 'allow', got {actions}"


def assert_deny(rule_func, event):
    """Assert that at least one DENY is present.

    Usage:
        assert_deny(bash_rules_bundle_universal, bash_event("git rm file.txt"))
    """
    results = eval_rule(rule_func, event)
    assert len(results) >= 1, f"Expected at least 1 decision, got {len(results)}"

    actions = [r.action for r in results]
    assert "deny" in actions, f"Expected at least one 'deny', got {actions}"


def assert_deny_count(rule_func, event, count):
    """Assert that rule yields exactly N deny decisions.

    Usage:
        assert_deny_count(rm_safe_operations_rule, bash_event("rm -rf /"), 2)
    """
    results = eval_rule(rule_func, event)
    assert len(results) == count, f"Expected {count} denies, got {len(results)}"
    for i, result in enumerate(results):
        assert result.action == "deny", f"Decision {i} expected 'deny', got '{result.action}'"


def assert_ask(rule_func, event):
    """Assert that at least one ASK is present.

    Usage:
        assert_ask(bash_rules_bundle_universal, bash_event("sqlite3 db.sqlite '.schema'"))
    """
    results = eval_rule(rule_func, event)
    assert len(results) >= 1, f"Expected at least 1 decision, got {len(results)}"

    actions = [r.action for r in results]
    assert "ask" in actions, f"Expected at least one 'ask', got {actions}"


def assert_pass(rule_func, event):
    """Assert that rule or bundle returns no decisions or guidance (passes through).

    Usage:
        assert_pass(comment_ratio_rule, file_edit_event("test.py", []))
        assert_pass(bash_rules_bundle_universal, bash_event("git status"))
    """
    try:
        results = list(rule_func(event))
    except TypeError:
        if hasattr(event, 'tool_is_bash') and event.tool_is_bash:
            try:
                parsed = BashCommandParser.parse(event.command)
            except ParseError:
                parsed = None
            results = list(rule_func(event, parsed))
        elif hasattr(event, 'tool_is_bash'):
            results = list(rule_func(event, None))
        else:
            results = list(rule_func(event))
    assert len(results) == 0, f"Expected no results (pass), got {len(results)}"


def assert_guidance(rule_func, event):
    """Assert that rule or bundle provides guidance.

    Usage:
        assert_guidance(legacy_code_rule, file_edit_event("test.py", ["DEPRECATED"]))
    """
    try:
        results = list(rule_func(event))
    except TypeError:
        if hasattr(event, 'tool_is_bash') and event.tool_is_bash:
            try:
                parsed = BashCommandParser.parse(event.command)
            except ParseError:
                parsed = None
            results = list(rule_func(event, parsed))
        else:
            results = list(rule_func(event))
    assert len(results) >= 1, f"Expected at least 1 guidance, got {len(results)}"
