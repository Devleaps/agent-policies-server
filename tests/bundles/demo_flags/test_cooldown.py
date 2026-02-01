"""Tests for demo_flags cooldown pattern."""

import pytest
from src.server.session import get_flag, clear_flags, initialize_flags_storage
from src.server.executor import execute_handlers_generic


@pytest.fixture(autouse=True)
def setup_demo():
    """Initialize flags storage and clear session before each test."""
    initialize_flags_storage()
    yield
    clear_flags("test-session")


def test_gh_pr_create_denied_first_time(bash_event):
    """Test that gh pr create is denied on first attempt."""
    event = bash_event("gh pr create --title 'Test'", bundles=["universal", "demo_flags"])
    results = list(execute_handlers_generic(event))

    # Should have a deny decision
    denies = [r for r in results if hasattr(r, 'action') and r.action == "deny"]
    assert len(denies) > 0
    assert any("PULL_REQUEST_TEMPLATE" in r.reason for r in denies if hasattr(r, 'reason') and r.reason)

    # Cooldown flag should be set
    assert get_flag("test-session", "pr_template_cooldown") is True


def test_gh_pr_create_allowed_during_cooldown(bash_event):
    """Test that gh pr create is allowed during cooldown period."""
    # First attempt - denied and sets cooldown
    first_event = bash_event("gh pr create --title 'Test'", bundles=["universal", "demo_flags"])
    list(execute_handlers_generic(first_event))

    # Second attempt - should be allowed (no deny rule fires)
    second_event = bash_event("gh pr create --title 'Test 2'", bundles=["universal", "demo_flags"])
    results = list(execute_handlers_generic(second_event))

    # Should not have the template deny decision
    denies = [r for r in results if hasattr(r, 'action') and r.action == "deny" and hasattr(r, 'reason') and r.reason and "PULL_REQUEST_TEMPLATE" in r.reason]
    assert len(denies) == 0


def test_cooldown_expires_after_10_invocations(bash_event):
    """Test that cooldown flag expires after 10 invocations."""
    # First attempt - sets cooldown
    first_event = bash_event("gh pr create --title 'Test'", bundles=["universal", "demo_flags"])
    list(execute_handlers_generic(first_event))

    # Simulate 10 invocations
    for i in range(10):
        event = bash_event("ls", bundles=["universal", "demo_flags"])
        list(execute_handlers_generic(event))

    # Cooldown should be expired
    assert get_flag("test-session", "pr_template_cooldown") is False

    # Next gh pr create should be denied again
    next_event = bash_event("gh pr create --title 'After cooldown'", bundles=["universal", "demo_flags"])
    results = list(execute_handlers_generic(next_event))

    denies = [r for r in results if hasattr(r, 'action') and r.action == "deny" and hasattr(r, 'reason') and r.reason and "PULL_REQUEST_TEMPLATE" in r.reason]
    assert len(denies) > 0


def test_cooldown_resets_on_each_first_attempt(bash_event):
    """Test that each first attempt after cooldown expires resets the cooldown."""
    # First cycle
    event1 = bash_event("gh pr create --title 'Test 1'", bundles=["universal", "demo_flags"])
    list(execute_handlers_generic(event1))

    # Wait for cooldown to expire
    for i in range(10):
        event = bash_event("ls", bundles=["universal", "demo_flags"])
        list(execute_handlers_generic(event))

    # Second cycle - should deny and reset cooldown
    event2 = bash_event("gh pr create --title 'Test 2'", bundles=["universal", "demo_flags"])
    results = list(execute_handlers_generic(event2))

    denies = [r for r in results if hasattr(r, 'action') and r.action == "deny" and hasattr(r, 'reason') and r.reason and "PULL_REQUEST_TEMPLATE" in r.reason]
    assert len(denies) > 0

    # Cooldown should be set again
    assert get_flag("test-session", "pr_template_cooldown") is True
