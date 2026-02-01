"""Tests for session flag management."""

import time
import pytest
from unittest.mock import patch
from src.server.session import (
    set_flag,
    get_flag,
    cleanup_expired_flags,
    decrement_invocation_flags,
    clear_flags,
    get_all_flags,
    initialize_flags_storage
)


@pytest.fixture(autouse=True)
def setup_flags():
    """Initialize flags storage before each test."""
    initialize_flags_storage()
    yield
    # No cleanup needed - each test uses unique session IDs


def test_set_and_get_flag_with_value():
    """Test setting and getting a flag with a specific value."""
    session_id = "test-session-1"

    set_flag(session_id, {"name": "test_flag", "value": True})
    assert get_flag(session_id, "test_flag") is True
    assert get_flag(session_id, "test_flag", True) is True
    assert get_flag(session_id, "test_flag", False) is False


def test_set_and_get_valueless_flag():
    """Test setting and getting a presence-only flag."""
    session_id = "test-session-2"

    set_flag(session_id, {"name": "presence_flag"})
    assert get_flag(session_id, "presence_flag") is True
    # Value defaults to True for presence-only flags
    assert get_flag(session_id, "presence_flag", True) is True


def test_get_nonexistent_flag():
    """Test getting a flag that doesn't exist returns False."""
    session_id = "test-session-3"

    assert get_flag(session_id, "nonexistent") is False
    assert get_flag(session_id, "nonexistent", "any_value") is False


def test_flag_overwriting():
    """Test that setting a flag twice overwrites the previous value."""
    session_id = "test-session-4"

    set_flag(session_id, {"name": "counter", "value": 1})
    assert get_flag(session_id, "counter", 1) is True

    set_flag(session_id, {"name": "counter", "value": 2})
    assert get_flag(session_id, "counter", 1) is False
    assert get_flag(session_id, "counter", 2) is True


def test_invocation_based_expiration():
    """Test flag expiration by invocation count."""
    session_id = "test-session-5"

    # Set flag that expires after 3 invocations
    set_flag(session_id, {
        "name": "invocation_flag",
        "value": True,
        "expires_after": 3,
        "expires_unit": "invocations"
    })

    # Flag should exist initially
    assert get_flag(session_id, "invocation_flag") is True

    # Decrement 3 times
    decrement_invocation_flags(session_id)
    assert get_flag(session_id, "invocation_flag") is True  # 2 remaining

    decrement_invocation_flags(session_id)
    assert get_flag(session_id, "invocation_flag") is True  # 1 remaining

    decrement_invocation_flags(session_id)
    assert get_flag(session_id, "invocation_flag") is False  # 0 remaining (expired)


def test_time_based_expiration():
    """Test flag expiration by time."""
    session_id = "test-session-6"

    with patch('src.server.session.time.time') as mock_time:
        mock_time.return_value = 1000.0

        set_flag(session_id, {
            "name": "time_flag",
            "value": True,
            "expires_after": 1,
            "expires_unit": "seconds"
        })

        assert get_flag(session_id, "time_flag") is True

        # Advance time by 1.1 seconds
        mock_time.return_value = 1001.1

        assert get_flag(session_id, "time_flag") is False


def test_immediate_expiration():
    """Test flag with expires_after=0 expires immediately."""
    session_id = "test-session-7"

    set_flag(session_id, {
        "name": "immediate",
        "expires_after": 0,
        "expires_unit": "invocations"
    })

    # Should be expired immediately
    assert get_flag(session_id, "immediate") is False


def test_cleanup_expired_flags():
    """Test cleanup removes expired flags."""
    session_id = "test-session-8"

    # Set two flags: one expired, one active
    set_flag(session_id, {
        "name": "expired",
        "expires_after": 0,
        "expires_unit": "invocations"
    })
    set_flag(session_id, {"name": "active", "value": True})

    cleanup_expired_flags(session_id)

    # Only active flag should remain
    flags = get_all_flags(session_id)
    assert "expired" not in flags
    assert "active" in flags
    assert flags["active"] is True


def test_get_all_flags():
    """Test getting all active flags for a session."""
    session_id = "test-session-9"

    set_flag(session_id, {"name": "flag1", "value": "value1"})
    set_flag(session_id, {"name": "flag2", "value": 42})
    set_flag(session_id, {"name": "flag3"})

    flags = get_all_flags(session_id)
    assert len(flags) == 3
    assert flags["flag1"] == "value1"
    assert flags["flag2"] == 42
    assert flags["flag3"] is True


def test_clear_flags():
    """Test clearing all flags for a session."""
    session_id = "test-session-10"

    set_flag(session_id, {"name": "flag1", "value": True})
    set_flag(session_id, {"name": "flag2", "value": True})

    clear_flags(session_id)

    assert get_flag(session_id, "flag1") is False
    assert get_flag(session_id, "flag2") is False
    assert get_all_flags(session_id) == {}


def test_multiple_sessions_isolated():
    """Test that flags in different sessions are isolated."""
    session1 = "session-1"
    session2 = "session-2"

    set_flag(session1, {"name": "flag", "value": "session1"})
    set_flag(session2, {"name": "flag", "value": "session2"})

    assert get_flag(session1, "flag", "session1") is True
    assert get_flag(session1, "flag", "session2") is False

    assert get_flag(session2, "flag", "session2") is True
    assert get_flag(session2, "flag", "session1") is False


def test_no_expiration_flag_persists():
    """Test that flags without expiration persist indefinitely."""
    session_id = "test-session-11"

    set_flag(session_id, {"name": "persistent", "value": True})

    # Decrement many times
    for _ in range(100):
        decrement_invocation_flags(session_id)

    # Flag should still exist
    assert get_flag(session_id, "persistent") is True

    # Cleanup shouldn't remove it
    cleanup_expired_flags(session_id)
    assert get_flag(session_id, "persistent") is True
