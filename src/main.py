#!/usr/bin/env python3
"""
Run the AI Agent Policy Server with all policy handlers registered.

Sets up policy enforcement handlers and starts the FastAPI server.
"""

import uvicorn

from src.server.server import app, get_registry
from src.server.models import ToolUseEvent, FileEditEvent, PostFileEditEvent, PostToolUseEvent

from src.evaluation import evaluate_bash_rules, evaluate_guidance


def setup_all_policies():
    """Register all policy handlers with the global registry."""
    registry = get_registry()

    # Single evaluators - bundle filtering happens in Rego based on event.enabled_bundles
    registry.register_handler(ToolUseEvent, evaluate_bash_rules)
    registry.register_handler(PostFileEditEvent, evaluate_guidance)

    print("All policies and guidance registered successfully!")


def main():
    """Start the server with all policies registered."""
    print("Starting AI Agent Policy Server...")

    setup_all_policies()

    print("Server ready with policy enforcement active!")
    print("Starting server on http://localhost:8338")

    uvicorn.run(app, host="0.0.0.0", port=8338, log_level="info")


if __name__ == "__main__":
    main()
