#!/usr/bin/env python3
"""
Run the AI Agent Policy Server with all policy handlers registered.

Sets up policy enforcement handlers and starts the FastAPI server.
"""

import uvicorn

from devleaps.policies.server.server import app, get_registry
from devleaps.policies.server.common.models import ToolUseEvent, FileEditEvent, PostFileEditEvent, PostToolUseEvent

# Session state management
from devleaps.policies.server.session import initialize_session_state

# Category-based policy packages
from src import cloud
from src import git
from src import js
from src import network
from src import python
from src import universal

# Bundle packages
from src import python_pip
from src import python_uv


def setup_all_policies():
    """Register all policy handlers and middleware with the global registry."""
    registry = get_registry()

    # Register middleware
    registry.register_all_middleware(ToolUseEvent, universal.all_middleware)
    registry.register_all_middleware(ToolUseEvent, git.all_middleware)
    registry.register_all_middleware(ToolUseEvent, python.all_middleware)

    registry.register_all_handlers(ToolUseEvent, universal.all_rules)
    registry.register_all_handlers(ToolUseEvent, cloud.all_rules)
    registry.register_all_handlers(ToolUseEvent, git.all_rules)
    registry.register_all_handlers(ToolUseEvent, js.all_rules)
    registry.register_all_handlers(ToolUseEvent, network.all_rules)
    registry.register_all_handlers(ToolUseEvent, python.all_rules)

    registry.register_all_handlers(ToolUseEvent, python_pip.all_rules, bundle="python-pip")
    registry.register_all_handlers(ToolUseEvent, python_uv.all_rules, bundle="python-uv")

    registry.register_all_handlers(PostFileEditEvent, python.all_post_file_edit_rules)
    registry.register_all_handlers(PostFileEditEvent, python_uv.all_post_file_edit_rules, bundle="python-uv")

    print("All policies and middleware registered successfully!")


def main():
    """Start the server with all policies registered."""
    print("Starting AI Agent Policy Server...")

    # Initialize session state storage
    initialize_session_state()
    print("Session state management initialized")

    setup_all_policies()

    print("Server ready with policy enforcement active!")
    print("Starting server on http://localhost:8338")

    uvicorn.run(app, host="0.0.0.0", port=8338, log_level="info")


if __name__ == "__main__":
    main()
