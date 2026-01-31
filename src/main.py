#!/usr/bin/env python3
"""
Run the AI Agent Policy Server with all policy handlers registered.

Sets up policy enforcement handlers and starts the FastAPI server.
"""

import uvicorn

from src.server.server import app, get_registry
from src.server.common.models import ToolUseEvent, FileEditEvent, PostFileEditEvent, PostToolUseEvent
from src.server.session import initialize_session_state

from src.bundles_impl import (
    bash_rules_bundle_universal,
    bash_rules_bundle_python_pip,
    bash_rules_bundle_python_uv,
    all_guidance_rules,
    all_python_uv_guidance_rules,
)


def setup_all_policies():
    """Register all policy handlers with the global registry."""
    registry = get_registry()

    registry.register_handler(ToolUseEvent, bash_rules_bundle_universal, bundle="default")
    registry.register_handler(ToolUseEvent, bash_rules_bundle_python_pip, bundle="python-pip")
    registry.register_handler(ToolUseEvent, bash_rules_bundle_python_uv, bundle="python-uv")

    registry.register_all_handlers(PostFileEditEvent, all_guidance_rules)
    registry.register_all_handlers(PostFileEditEvent, all_python_uv_guidance_rules, bundle="python-uv")

    print("All policies and guidance registered successfully!")


def main():
    """Start the server with all policies registered."""
    print("Starting AI Agent Policy Server...")

    initialize_session_state()
    print("Session state management initialized")

    setup_all_policies()

    print("Server ready with policy enforcement active!")
    print("Starting server on http://localhost:8338")

    uvicorn.run(app, host="0.0.0.0", port=8338, log_level="info")


if __name__ == "__main__":
    main()
