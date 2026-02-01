"""Tests for demo_flags multi-step workflow."""

import pytest
from src.server.session.flags import get_flag, clear_flags, initialize_flags_storage
from src.server.executor import execute_handlers_generic


@pytest.fixture(autouse=True)
def setup_demo():
    """Initialize flags storage and clear session before each test."""
    initialize_flags_storage()
    yield
    clear_flags("test-session")


def test_lint_sets_passed_lint_flag(bash_event):
    """Test that running ruff check sets the passed_lint flag."""
    event = bash_event("ruff check .", bundles=["universal", "demo_flags"])
    list(execute_handlers_generic(event))

    assert get_flag("test-session", "passed_lint", True) is True


def test_pytest_denied_without_lint(bash_event):
    """Test that pytest is denied if lint hasn't been run."""
    event = bash_event("pytest tests/", bundles=["universal", "demo_flags"])
    results = list(execute_handlers_generic(event))

    denies = [r for r in results if hasattr(r, 'action') and r.action == "deny" and hasattr(r, 'reason') and r.reason and "ruff check" in r.reason.lower()]
    assert len(denies) > 0


def test_pytest_allowed_after_lint(bash_event):
    """Test that pytest is allowed after running lint."""
    # Run lint first
    lint_event = bash_event("ruff check .", bundles=["universal", "demo_flags"])
    list(execute_handlers_generic(lint_event))

    # Now pytest should be allowed
    pytest_event = bash_event("pytest tests/", bundles=["universal", "demo_flags"])
    results = list(execute_handlers_generic(pytest_event))

    denies = [r for r in results if hasattr(r, 'action') and r.action == "deny" and hasattr(r, 'reason') and r.reason and "ruff check" in r.reason.lower()]
    assert len(denies) == 0


def test_pytest_sets_passed_tests_flag(bash_event):
    """Test that pytest sets the passed_tests flag."""
    # Run lint first
    lint_event = bash_event("ruff check .", bundles=["universal", "demo_flags"])
    list(execute_handlers_generic(lint_event))

    # Run pytest
    pytest_event = bash_event("pytest tests/", bundles=["universal", "demo_flags"])
    list(execute_handlers_generic(pytest_event))

    assert get_flag("test-session", "passed_tests", True) is True


def test_docker_push_denied_without_lint(bash_event):
    """Test that docker push is denied if lint hasn't been run."""
    event = bash_event("docker push myimage:latest", bundles=["universal", "demo_flags"])
    results = list(execute_handlers_generic(event))

    denies = [r for r in results if hasattr(r, 'action') and r.action == "deny" and hasattr(r, 'reason') and r.reason and "lint" in r.reason.lower()]
    assert len(denies) > 0


def test_docker_push_denied_without_tests(bash_event):
    """Test that docker push is denied if tests haven't been run."""
    # Run lint only
    lint_event = bash_event("ruff check .", bundles=["universal", "demo_flags"])
    list(execute_handlers_generic(lint_event))

    # Try to push
    push_event = bash_event("docker push myimage:latest", bundles=["universal", "demo_flags"])
    results = list(execute_handlers_generic(push_event))

    denies = [r for r in results if hasattr(r, 'action') and r.action == "deny" and hasattr(r, 'reason') and r.reason and "test" in r.reason.lower()]
    assert len(denies) > 0


def test_docker_push_allowed_after_lint_and_tests(bash_event):
    """Test that docker push is allowed after running both lint and tests."""
    # Run lint
    lint_event = bash_event("ruff check .", bundles=["universal", "demo_flags"])
    list(execute_handlers_generic(lint_event))

    # Run tests
    pytest_event = bash_event("pytest tests/", bundles=["universal", "demo_flags"])
    list(execute_handlers_generic(pytest_event))

    # Now push should be allowed
    push_event = bash_event("docker push myimage:latest", bundles=["universal", "demo_flags"])
    results = list(execute_handlers_generic(push_event))

    # Should have an allow decision
    allows = [r for r in results if hasattr(r, 'action') and r.action == "allow"]
    # The demo_flags allow should be present (there may be other denies from other bundles)
    assert len(allows) > 0


def test_workflow_flag_expiration(bash_event):
    """Test that workflow flags expire after specified invocations."""
    # Run lint (expires after 50)
    lint_event = bash_event("ruff check .", bundles=["universal", "demo_flags"])
    list(execute_handlers_generic(lint_event))

    # Run tests (expires after 30)
    pytest_event = bash_event("pytest tests/", bundles=["universal", "demo_flags"])
    list(execute_handlers_generic(pytest_event))

    # Both flags should exist
    assert get_flag("test-session", "passed_lint", True) is True
    assert get_flag("test-session", "passed_tests", True) is True

    # Simulate 31 invocations
    for i in range(31):
        event = bash_event("ls", bundles=["universal", "demo_flags"])
        list(execute_handlers_generic(event))

    # passed_tests should be expired, but passed_lint should still exist
    assert get_flag("test-session", "passed_tests") is False
    assert get_flag("test-session", "passed_lint", True) is True

    # docker push should be denied (missing tests)
    push_event = bash_event("docker push myimage:latest", bundles=["universal", "demo_flags"])
    results = list(execute_handlers_generic(push_event))

    denies = [r for r in results if hasattr(r, 'action') and r.action == "deny" and hasattr(r, 'reason') and r.reason and "test" in r.reason.lower()]
    assert len(denies) > 0
