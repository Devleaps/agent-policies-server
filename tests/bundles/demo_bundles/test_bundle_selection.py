"""Tests for demo_bundles bundle_selection policy."""

import pytest
from src.evaluation.handlers import evaluate_bash_rules
from src.server.models import PolicyAction


def test_denies_when_neither_python_bundle_active(bash_event):
    """When demo_bundles is active but neither python_pip nor python_uv is, deny."""
    event = bash_event("ls", bundles=["universal", "demo_bundles"])
    results = list(evaluate_bash_rules(event))
    deny = [r for r in results if hasattr(r, "action") and r.action == PolicyAction.DENY]
    assert deny, "Expected a deny when no Python package manager bundle is active"
    assert "python_pip" in deny[0].reason
    assert "python_uv" in deny[0].reason


def test_no_deny_when_python_pip_active(bash_event):
    """When python_pip is active, no deny from bundle_selection."""
    event = bash_event("ls", bundles=["universal", "demo_bundles", "python_pip"])
    results = list(evaluate_bash_rules(event))
    deny = [r for r in results if hasattr(r, "action") and r.action == PolicyAction.DENY
            and r.reason and "package manager bundle" in r.reason]
    assert not deny


def test_no_deny_when_python_uv_active(bash_event):
    """When python_uv is active, no deny from bundle_selection."""
    event = bash_event("ls", bundles=["universal", "demo_bundles", "python_uv"])
    results = list(evaluate_bash_rules(event))
    deny = [r for r in results if hasattr(r, "action") and r.action == PolicyAction.DENY
            and r.reason and "package manager bundle" in r.reason]
    assert not deny


def test_no_deny_when_both_python_bundles_active(bash_event):
    """When both python_pip and python_uv are active, no deny from bundle_selection."""
    event = bash_event("ls", bundles=["universal", "demo_bundles", "python_pip", "python_uv"])
    results = list(evaluate_bash_rules(event))
    deny = [r for r in results if hasattr(r, "action") and r.action == PolicyAction.DENY
            and r.reason and "package manager bundle" in r.reason]
    assert not deny


def test_no_deny_without_demo_bundles(bash_event):
    """Without demo_bundles, the rule is not evaluated at all."""
    event = bash_event("ls", bundles=["universal"])
    results = list(evaluate_bash_rules(event))
    deny = [r for r in results if hasattr(r, "action") and r.action == PolicyAction.DENY
            and r.reason and "package manager bundle" in r.reason]
    assert not deny
