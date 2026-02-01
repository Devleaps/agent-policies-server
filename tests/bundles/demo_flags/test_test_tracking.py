"""Tests for demo_flags test tracking policies."""

import pytest
from src.bundles_impl import evaluate_bash_rules
from src.server.session.flags import get_flag, clear_flags, initialize_flags_storage
from src.server.executor import execute_handlers_generic
from tests.helpers import assert_allow, assert_deny


@pytest.fixture(autouse=True)
def setup_demo():
    """Initialize flags storage and clear session before each test."""
    initialize_flags_storage()
    yield
    clear_flags("test-session")


def test_pytest_sets_ran_tests_flag(bash_event):
    """Test that running pytest sets the ran_tests flag."""
    event = bash_event("pytest tests/", bundles=["universal", "demo_flags"])

    # Execute policies (which processes flags)
    results = list(execute_handlers_generic(event))

    # Check that flag was set
    assert get_flag(event.session_id, "ran_tests", True) is True


def test_commit_denied_without_tests(bash_event):
    """Test that git commit is denied if tests haven't been run."""
    # Clear any existing flags
    clear_flags("test-session")

    event = bash_event("git commit -m 'test'", bundles=["universal", "demo_flags"])
    results = list(execute_handlers_generic(event))

    # Should have a deny decision
    denies = [r for r in results if hasattr(r, 'action') and r.action == "deny"]
    assert len(denies) > 0
    assert any("pytest" in r.reason.lower() for r in denies if hasattr(r, 'reason') and r.reason)


def test_commit_allowed_after_tests(bash_event):
    """Test that git commit is allowed after running tests."""
    # First run pytest
    pytest_event = bash_event("pytest tests/", bundles=["universal", "demo_flags"])
    list(execute_handlers_generic(pytest_event))

    # Verify flag was set
    assert get_flag("test-session", "ran_tests", True) is True

    # Now try to commit
    commit_event = bash_event("git commit -m 'test'", bundles=["universal", "demo_flags"])
    results = list(execute_handlers_generic(commit_event))

    # Should not have the pytest deny decision
    denies = [r for r in results if hasattr(r, 'action') and r.action == "deny" and hasattr(r, 'reason') and r.reason and "pytest" in r.reason.lower()]
    assert len(denies) == 0


def test_file_edit_invalidates_test_flag(bash_event, file_edit_event):
    """Test that editing a Python file invalidates the ran_tests flag."""
    # First run pytest to set the flag
    pytest_event = bash_event("pytest tests/", bundles=["universal", "demo_flags"])
    list(execute_handlers_generic(pytest_event))
    assert get_flag("test-session", "ran_tests", True) is True

    # Edit a Python file
    edit_event = file_edit_event("test.py", ["# comment", "code = 1"], bundles=["universal", "demo_flags"])
    list(execute_handlers_generic(edit_event))

    # Flag should now be False
    assert get_flag("test-session", "ran_tests", False) is True
    assert get_flag("test-session", "ran_tests", True) is False

    # Commit should be denied again
    commit_event = bash_event("git commit -m 'test'", bundles=["universal", "demo_flags"])
    results = list(execute_handlers_generic(commit_event))

    denies = [r for r in results if hasattr(r, 'action') and r.action == "deny" and hasattr(r, 'reason') and r.reason and "pytest" in r.reason.lower()]
    assert len(denies) > 0


def test_ran_tests_flag_expires_after_100_invocations(bash_event):
    """Test that the ran_tests flag expires after 100 invocations."""
    # Run pytest to set the flag
    pytest_event = bash_event("pytest tests/", bundles=["universal", "demo_flags"])
    list(execute_handlers_generic(pytest_event))

    # Flag should exist
    assert get_flag("test-session", "ran_tests", True) is True

    # Simulate 100 invocations by running 100 commands
    for i in range(100):
        event = bash_event("ls", bundles=["universal", "demo_flags"])
        list(execute_handlers_generic(event))

    # Flag should be expired
    assert get_flag("test-session", "ran_tests") is False

    # Commit should be denied again
    commit_event = bash_event("git commit -m 'test'", bundles=["universal", "demo_flags"])
    results = list(execute_handlers_generic(commit_event))

    denies = [r for r in results if hasattr(r, 'action') and r.action == "deny" and hasattr(r, 'reason') and r.reason and "pytest" in r.reason.lower()]
    assert len(denies) > 0
