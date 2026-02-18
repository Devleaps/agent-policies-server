"""
Session flag management for policy enforcement.

Provides flag setting/checking with invocation count and time-based expiration.
Thread-safe storage keyed by session ID.
"""

import time
import threading
from typing import Any, Dict, Optional
from dataclasses import dataclass

# Thread lock for flag operations
_flags_lock = threading.Lock()

# Global flag storage (keyed by session_id)
_session_flags: Dict[str, Dict[str, "Flag"]] = {}


@dataclass
class Flag:
    """Represents a session flag with optional expiration."""

    name: str
    value: Any = True
    expires_after: Optional[int] = None
    expires_unit: Optional[str] = None

    created_at: Optional[float] = None
    invocations_remaining: Optional[int] = None

    def __post_init__(self):
        """Initialize created_at and invocation counter."""
        if self.created_at is None:
            self.created_at = time.time()
        if self.expires_unit == "invocations" and self.expires_after is not None:
            self.invocations_remaining = self.expires_after

    def is_expired(self) -> bool:
        """Check if flag has expired."""
        if self.expires_after is None:
            return False

        if self.expires_after == 0:
            return True

        if self.expires_unit == "seconds":
            created_at = self.created_at if self.created_at is not None else 0.0
            return (time.time() - created_at) >= self.expires_after
        elif self.expires_unit == "invocations":
            return (
                self.invocations_remaining is not None
                and self.invocations_remaining <= 0
            )

        return False

    def decrement_invocation(self):
        """Decrement invocation counter if applicable."""
        if (
            self.expires_unit == "invocations"
            and self.invocations_remaining is not None
        ):
            self.invocations_remaining -= 1


def initialize_flags_storage():
    """Initialize flags storage."""
    # Already initialized as module-level dict
    pass


def set_flag(session_id: str, flag_spec: Dict[str, Any]) -> None:
    """
    Set a flag for a session.

    Args:
        session_id: Session identifier
        flag_spec: Flag specification dict with keys:
            - name (required): Flag name
            - value (optional): Flag value (default: True)
            - expires_after (optional): Expiration count/duration
            - expires_unit (optional): "invocations" or "seconds"
    """
    with _flags_lock:
        if session_id not in _session_flags:
            _session_flags[session_id] = {}

        flag = Flag(
            name=flag_spec["name"],
            value=flag_spec.get("value", True),
            expires_after=flag_spec.get("expires_after"),
            expires_unit=flag_spec.get("expires_unit"),
        )

        _session_flags[session_id][flag_spec["name"]] = flag


def get_flag(session_id: str, name: str, value: Any = None) -> bool:
    """
    Check if a flag exists and optionally matches a value.

    Args:
        session_id: Session identifier
        name: Flag name to check
        value: If provided, also check if flag value matches

    Returns:
        True if flag exists (and matches value if provided), False otherwise
    """
    with _flags_lock:
        if session_id not in _session_flags:
            return False

        flag = _session_flags[session_id].get(name)
        if flag is None or flag.is_expired():
            return False

        if value is None:
            return True

        return flag.value == value


def cleanup_expired_flags(session_id: str) -> None:
    """
    Remove expired flags for a session.

    Args:
        session_id: Session identifier
    """
    with _flags_lock:
        if session_id not in _session_flags:
            return

        expired = [
            name
            for name, flag in _session_flags[session_id].items()
            if flag.is_expired()
        ]

        for name in expired:
            del _session_flags[session_id][name]


def decrement_invocation_flags(session_id: str) -> None:
    """
    Decrement invocation counters for all invocation-based flags.

    Args:
        session_id: Session identifier
    """
    with _flags_lock:
        if session_id not in _session_flags:
            return

        for flag in _session_flags[session_id].values():
            flag.decrement_invocation()


def clear_flags(session_id: str) -> None:
    """
    Clear all flags for a session.

    Args:
        session_id: Session identifier
    """
    with _flags_lock:
        if session_id in _session_flags:
            del _session_flags[session_id]


def get_all_flags(session_id: str) -> Dict[str, Any]:
    """
    Get all active (non-expired) flags for a session.

    Args:
        session_id: Session identifier

    Returns:
        Dict mapping flag names to their values
    """
    with _flags_lock:
        if session_id not in _session_flags:
            return {}

        return {
            name: flag.value
            for name, flag in _session_flags[session_id].items()
            if not flag.is_expired()
        }
