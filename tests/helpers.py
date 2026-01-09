"""Helper functions for evaluating rules and asserting results."""


def eval_rule(rule_func, event):
    """Evaluate a rule function with an event and return decisions only.

    Usage:
        results = eval_rule(git_add_rule, bash_event("git add file.txt"))
        assert_allow(results)
    """
    results = list(rule_func(event))
    return [r for r in results if hasattr(r, 'action')]


def assert_allow(rule_func, event):
    """Assert that rule allows the action.

    Usage:
        assert_allow(git_add_rule, bash_event("git add file.txt"))
    """
    results = eval_rule(rule_func, event)
    assert len(results) == 1, f"Expected 1 decision, got {len(results)}"
    assert results[0].action == "allow", f"Expected 'allow', got '{results[0].action}'"


def assert_deny(rule_func, event, reason_contains=None):
    """Assert that rule denies the action with optional reason check.

    Usage:
        assert_deny(git_rm_rule, bash_event("git rm file.txt"))
        assert_deny(git_rm_rule, bash_event("git rm file.txt"), "not allowed")
    """
    results = eval_rule(rule_func, event)
    assert len(results) >= 1, f"Expected at least 1 decision, got {len(results)}"
    assert results[0].action == "deny", f"Expected 'deny', got '{results[0].action}'"
    if reason_contains:
        assert reason_contains.lower() in results[0].reason.lower(), \
            f"Expected reason to contain '{reason_contains}', got: {results[0].reason}"


def assert_deny_count(rule_func, event, count):
    """Assert that rule yields exactly N deny decisions.

    Usage:
        assert_deny_count(rm_safe_operations_rule, bash_event("rm -rf /"), 2)
    """
    results = eval_rule(rule_func, event)
    assert len(results) == count, f"Expected {count} denies, got {len(results)}"
    for i, result in enumerate(results):
        assert result.action == "deny", f"Decision {i} expected 'deny', got '{result.action}'"


def assert_ask(rule_func, event, reason_contains=None):
    """Assert that rule asks for confirmation.

    Usage:
        assert_ask(sqlite3_rule, bash_event("sqlite3 db.sqlite '.schema'"))
    """
    results = eval_rule(rule_func, event)
    assert len(results) == 1, f"Expected 1 decision, got {len(results)}"
    assert results[0].action == "ask", f"Expected 'ask', got '{results[0].action}'"
    if reason_contains:
        assert reason_contains.lower() in results[0].reason.lower(), \
            f"Expected reason to contain '{reason_contains}', got: {results[0].reason}"


def assert_pass(rule_func, event):
    """Assert that rule returns no decisions or guidance (passes through).

    Usage:
        assert_pass(comment_ratio_rule, file_edit_event("test.py", []))
        assert_pass(git_add_rule, bash_event("git status"))
    """
    results = list(rule_func(event))
    assert len(results) == 0, f"Expected no results (pass), got {len(results)}"


def assert_guidance(rule_func, event, content_contains=None):
    """Assert that rule provides guidance with optional content check.

    Usage:
        assert_guidance(legacy_code_rule, file_edit_event("test.py", ["DEPRECATED"]))
        assert_guidance(legacy_code_rule, event, "deprecated")
    """
    results = list(rule_func(event))
    assert len(results) == 1, f"Expected 1 guidance, got {len(results)}"
    if content_contains:
        assert content_contains.lower() in results[0].content.lower(), \
            f"Expected content to contain '{content_contains}', got: {results[0].content}"
