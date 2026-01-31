"""Tests for python_pip bundle policies."""

import pytest
from src.bundles_impl import evaluate_bash_rules
from tests.helpers import assert_allow, assert_deny, assert_pass


def test_pip_install_with_old_package(bash_event):
    """Test pip install allows packages older than 1 year."""
    assert_allow(evaluate_bash_rules, bash_event("pip install requests", bundles=["universal", "python_pip"]))
    assert_allow(evaluate_bash_rules, bash_event("pip install httpx", bundles=["universal", "python_pip"]))


def test_pip_install_with_new_package(bash_event):
    """Test pip install denies packages newer than 1 year."""
    assert_deny(evaluate_bash_rules, bash_event("pip install this-package-definitely-does-not-exist-12345", bundles=["universal", "python_pip"]))


def test_pip_install_requirements_txt_bypasses_validation(bash_event):
    """Test pip install -r requirements.txt is allowed without individual package validation."""
    event = bash_event("pip install -r requirements.txt", bundles=["universal", "python_pip"])
    assert_allow(evaluate_bash_rules, event)


def test_pip_install_non_bash_passes(bash_event):
    """Test non-bash events pass through."""
    event = bash_event("pip install requests", tool_is_bash=False, bundles=["universal", "python_pip"])
    assert_pass(evaluate_bash_rules, event)
    assert_pass(evaluate_bash_rules, event)
