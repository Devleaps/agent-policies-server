"""Tests for python-pip bundle policies."""

import pytest
from src.bundles_impl import bash_rules_bundle_python_pip
from tests.helpers import assert_allow, assert_deny, assert_pass


def test_pip_install_with_old_package(bash_event):
    """Test pip install allows packages older than 1 year."""
    assert_allow(bash_rules_bundle_python_pip, bash_event("pip install requests"))
    assert_allow(bash_rules_bundle_python_pip, bash_event("pip install httpx"))


def test_pip_install_with_new_package(bash_event):
    """Test pip install denies packages newer than 1 year."""
    assert_deny(bash_rules_bundle_python_pip, bash_event("pip install this-package-definitely-does-not-exist-12345"))


def test_pip_install_requirements_txt_bypasses_validation(bash_event):
    """Test pip install -r requirements.txt is allowed without individual package validation."""
    event = bash_event("pip install -r requirements.txt")
    assert_allow(bash_rules_bundle_python_pip, event)


def test_pip_install_non_bash_passes(bash_event):
    """Test non-bash events pass through."""
    event = bash_event("pip install requests", tool_is_bash=False)
    assert_pass(bash_rules_bundle_python_pip, event)
    assert_pass(bash_rules_bundle_python_pip, event)
