#!/usr/bin/env python3
"""
Run the AI Agent Policy Server with all policy handlers registered.

Sets up policy enforcement handlers and starts the FastAPI server.
"""

import uvicorn

from src.config import settings
from src.server.server import app, get_registry
from src.server.models import ToolUseEvent, PostFileEditEvent

from src.evaluation import evaluate_bash_rules, evaluate_webfetch_rules, evaluate_guidance


def setup_all_policies():
    """Register all policy handlers with the global registry."""
    registry = get_registry()

    # Single evaluators - bundle filtering happens in Rego based on event.enabled_bundles
    registry.register_handler(ToolUseEvent, evaluate_bash_rules)
    registry.register_handler(ToolUseEvent, evaluate_webfetch_rules)
    registry.register_handler(PostFileEditEvent, evaluate_guidance)

    print("All policies and guidance registered successfully!")


def main():
    """Start the server with all policies registered."""
    print("Starting AI Agent Policy Server...")

    setup_all_policies()

    print("Server ready with policy enforcement active!")
    print(f"Starting server on http://{settings.host}:{settings.port}")

    uvicorn.run(app, host=settings.host, port=settings.port, log_level="info")


if __name__ == "__main__":
    main()
