"""
Session state management implementation.

Provides thread-safe session state storage using module-level dict.
"""

import threading
from typing import Any, Dict, Optional, Union

from ..common.models import BaseEvent


# Thread lock for session state access
_state_lock = threading.Lock()

# Global session storage (keyed by session_id)
_sessions: Dict[str, Dict[str, Any]] = {}


def initialize_session_state():
    """
    Initialize the session state storage.

    Should be called once at server startup before any policies are registered.
    """
    # Already initialized as module-level dict
    pass


def get_session_state(event: BaseEvent) -> Dict[str, Any]:
    """
    Get the full state dictionary for a session.

    Creates an empty state dict if the session doesn't exist.

    Args:
        event: The event containing session_id

    Returns:
        Dictionary containing all state for this session
    """
    session_id = event.session_id

    with _state_lock:
        if session_id not in _sessions:
            _sessions[session_id] = {}

        return _sessions[session_id].copy()


def set_session_flag(event: BaseEvent, key: str, value: Any) -> None:
    """
    Set a state flag/value for a session.

    Args:
        event: The event containing session_id
        key: The state key to set
        value: The value to store (can be any JSON-serializable type)
    """
    session_id = event.session_id

    with _state_lock:
        if session_id not in _sessions:
            _sessions[session_id] = {}

        _sessions[session_id][key] = value


def get_session_flag(event: BaseEvent, key: str, default: Any = None) -> Any:
    """
    Get a state flag/value for a session.

    Args:
        event: The event containing session_id
        key: The state key to get
        default: Default value if key doesn't exist

    Returns:
        The value stored for this key, or default if not found
    """
    session_id = event.session_id

    with _state_lock:
        if session_id not in _sessions:
            return default

        return _sessions[session_id].get(key, default)


def clear_session_state(event: BaseEvent) -> None:
    """
    Clear all state for a session.

    Args:
        event: The event containing session_id to clear
    """
    session_id = event.session_id

    with _state_lock:
        if session_id in _sessions:
            del _sessions[session_id]


def list_sessions() -> list[str]:
    """
    List all active session IDs.

    Returns:
        List of session IDs that have state stored
    """
    with _state_lock:
        return list(_sessions.keys())
