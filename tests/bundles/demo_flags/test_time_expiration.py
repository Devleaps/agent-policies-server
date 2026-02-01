"""Tests for demo_flags time-based expiration."""

import time
import pytest
from unittest.mock import patch
from src.server.session import get_flag, clear_flags, initialize_flags_storage
from src.server.executor import execute_handlers_generic


@pytest.fixture(autouse=True)
def setup_demo():
    """Initialize flags storage and clear session before each test."""
    initialize_flags_storage()
    yield
    clear_flags("test-session")


def test_docker_build_sets_cache_flag(bash_event):
    """Test that docker build sets the build_cached flag."""
    event = bash_event("docker build -t myimage:latest .", bundles=["universal", "demo_flags"])
    list(execute_handlers_generic(event))

    assert get_flag("test-session", "build_cached", True) is True


def test_docker_push_asks_without_build_cache(bash_event):
    """Test that docker push asks if build cache doesn't exist."""
    event = bash_event("docker push myimage:latest", bundles=["universal", "demo_flags"])
    results = list(execute_handlers_generic(event))

    asks = [r for r in results if hasattr(r, 'action') and r.action == "ask" and hasattr(r, 'reason') and r.reason and "build" in r.reason.lower()]
    assert len(asks) > 0


def test_docker_push_allowed_with_build_cache(bash_event):
    """Test that docker push is allowed if build cache exists."""
    # Build first
    build_event = bash_event("docker build -t myimage:latest .", bundles=["universal", "demo_flags"])
    list(execute_handlers_generic(build_event))

    # Push should be allowed
    push_event = bash_event("docker push myimage:latest", bundles=["universal", "demo_flags"])
    results = list(execute_handlers_generic(push_event))

    # Should have allow decisions (may have denies from other bundles, but not the cache ask)
    asks = [r for r in results if hasattr(r, 'action') and r.action == "ask" and hasattr(r, 'reason') and r.reason and "build" in r.reason.lower()]
    assert len(asks) == 0


def test_build_cache_expires_after_2_seconds(bash_event):
    """Test that build_cached flag expires after 2 seconds."""
    with patch('src.server.session.time.time') as mock_time:
        mock_time.return_value = 1000.0

        build_event = bash_event("docker build -t myimage:latest .", bundles=["universal", "demo_flags"])
        list(execute_handlers_generic(build_event))

        assert get_flag("test-session", "build_cached", True) is True

        # Advance time by 3 seconds
        mock_time.return_value = 1003.0

        assert get_flag("test-session", "build_cached") is False

        push_event = bash_event("docker push myimage:latest", bundles=["universal", "demo_flags"])
        results = list(execute_handlers_generic(push_event))

        asks = [r for r in results if hasattr(r, 'action') and r.action == "ask" and hasattr(r, 'reason') and r.reason and "build" in r.reason.lower()]
        assert len(asks) > 0


def test_immediate_expiration(bash_event):
    """Test that echo one-time sets a flag that expires immediately."""
    event = bash_event("echo one-time", bundles=["universal", "demo_flags"])
    list(execute_handlers_generic(event))

    # Flag should be expired immediately (expires_after: 0)
    assert get_flag("test-session", "echo_fired") is False
