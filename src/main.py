#!/usr/bin/env python3
"""
Run the AI Agent Policy Server with all policy handlers registered.

Sets up policy enforcement handlers and starts the FastAPI server.
"""

import uvicorn

from devleaps.policies.server.server import app, get_registry
from devleaps.policies.server.common.models import ToolUseEvent

# Common policies (consolidated)
from src.common import whitelist_always, whitelist_safe_paths

# Middleware modules
from src import bash
from src import time
from src import timeout
from src import uv

# Command-specific policies
from src import find
from src import az
from src import python
from src import virtualenv
from src import pip
from src import webfetch
from src import websearch
from src import terraform
from src import terragrunt
from src import yarn
from src import mv
from src import rm
from src import rmdir
from src import git
from src import curl
from src import sudo
from src import cd
from src import sleep
from src import kill
from src import kubectl
from src import python3


def setup_all_policies():
    """Register all policy handlers and middleware with the global registry."""
    registry = get_registry()

    # Register all middleware
    registry.register_all_middleware(ToolUseEvent, bash.all_middleware)
    registry.register_all_middleware(ToolUseEvent, time.all_middleware)
    registry.register_all_middleware(ToolUseEvent, timeout.all_middleware)
    registry.register_all_middleware(ToolUseEvent, uv.all_middleware)

    # Common policies (consolidated rules for multiple commands)
    registry.register_all_handlers(ToolUseEvent, whitelist_always.all_rules)
    registry.register_all_handlers(ToolUseEvent, whitelist_safe_paths.all_rules)

    # Command-specific policies
    registry.register_all_handlers(ToolUseEvent, find.all_rules)
    registry.register_all_handlers(ToolUseEvent, az.all_rules)
    registry.register_all_handlers(ToolUseEvent, python.all_rules)
    registry.register_all_handlers(ToolUseEvent, virtualenv.all_rules)
    registry.register_all_handlers(ToolUseEvent, pip.all_rules)
    registry.register_all_handlers(ToolUseEvent, webfetch.all_rules)
    registry.register_all_handlers(ToolUseEvent, websearch.all_rules)
    registry.register_all_handlers(ToolUseEvent, terraform.all_rules)
    registry.register_all_handlers(ToolUseEvent, terragrunt.all_rules)
    registry.register_all_handlers(ToolUseEvent, yarn.all_rules)
    registry.register_all_handlers(ToolUseEvent, mv.all_rules)
    registry.register_all_handlers(ToolUseEvent, rm.all_rules)
    registry.register_all_handlers(ToolUseEvent, rmdir.all_rules)
    registry.register_all_handlers(ToolUseEvent, git.all_rules)
    registry.register_all_handlers(ToolUseEvent, curl.all_rules)
    registry.register_all_handlers(ToolUseEvent, sudo.all_rules)
    registry.register_all_handlers(ToolUseEvent, cd.all_rules)
    registry.register_all_handlers(ToolUseEvent, sleep.all_rules)
    registry.register_all_handlers(ToolUseEvent, kill.all_rules)
    registry.register_all_handlers(ToolUseEvent, kubectl.all_rules)
    registry.register_all_handlers(ToolUseEvent, python3.all_rules)

    print("All policies and middleware registered successfully!")


def main():
    """Start the server with all policies registered."""
    print("Starting AI Agent Policy Server...")

    setup_all_policies()

    print("Server ready with policy enforcement active!")
    print("Starting server on http://localhost:8338")

    uvicorn.run(app, host="0.0.0.0", port=8338, log_level="info")


if __name__ == "__main__":
    main()
