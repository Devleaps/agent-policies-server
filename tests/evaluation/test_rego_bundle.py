"""The evaluator compiles policies once and serves every request from that bundle."""

import inspect
from concurrent.futures import ThreadPoolExecutor

import pytest

from src.evaluation.rego import ENTRYPOINT_RULES, RegoEvaluator
from src.evaluation.handlers import evaluate_bash_rules
from src.server.claude_code import routes as claude_code_routes
from src.server.cursor import routes as cursor_routes
from src.server.gemini import routes as gemini_routes


@pytest.fixture(scope="module")
def evaluator():
    return RegoEvaluator(policy_dir="policies")


def test_every_package_rule_set_is_an_entrypoint(evaluator):
    assert evaluator.bundle is not None
    for rule in ENTRYPOINT_RULES:
        assert f"universal/{rule}" in evaluator.entrypoints
        assert f"python_uv/{rule}" in evaluator.entrypoints
    assert "helpers/bundles/decisions" in evaluator.entrypoints


def test_unknown_bundle_yields_nothing(bash_event):
    decisions = [
        r
        for r in evaluate_bash_rules(bash_event("ls", bundles=["universal", "nope"]))
        if hasattr(r, "action")
    ]
    assert decisions
    assert all(d.action == "allow" for d in decisions)


def test_concurrent_evaluations_do_not_share_input(bash_event):
    commands = ["ls", "rm -rf /", "git status", "curl http://example.com", "pwd"] * 8

    def decide(command):
        results = evaluate_bash_rules(bash_event(command))
        return sorted({r.action for r in results if hasattr(r, "action")})

    expected = [decide(command) for command in commands]
    with ThreadPoolExecutor(max_workers=8) as pool:
        actual = list(pool.map(decide, commands))

    assert actual == expected


def test_hook_routes_run_in_the_threadpool():
    """Evaluation is CPU-bound, so hook endpoints are plain functions and the
    event loop stays free to answer health probes."""
    for module in (claude_code_routes, cursor_routes, gemini_routes):
        hooks = [
            fn
            for name, fn in inspect.getmembers(module, inspect.isfunction)
            if name.endswith("_hook")
        ]
        assert hooks
        for hook in hooks:
            assert not inspect.iscoroutinefunction(hook), hook.__name__
