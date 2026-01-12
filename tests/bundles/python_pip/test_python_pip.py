"""Tests for python-pip bundle policies."""

import pytest
from src.bundles.python_pip import bash_rules_bundle_python_pip
from src.bundles.python_pip.predicates import pypi_package_age_predicate
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


def test_pypi_package_age_predicate_direct():
    """Test pypi_package_age_predicate function directly."""
    allowed, reason = pypi_package_age_predicate("requests")
    assert allowed is True
    assert "year" in reason.lower()

    allowed, reason = pypi_package_age_predicate("this-does-not-exist-12345")
    assert allowed is False
    assert "not found" in reason.lower() or "failed" in reason.lower()
