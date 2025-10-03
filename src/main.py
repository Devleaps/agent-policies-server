#!/usr/bin/env python3
"""
Run the AI Agent Policy Server with all policy handlers registered.

Sets up policy enforcement handlers and starts the FastAPI server.
"""

import uvicorn

from devleaps.policies.server.server import app, get_registry
from devleaps.policies.server.common.models import ToolUseEvent
from src import find
from src import az
from src import python
from src import pytest
from src import virtualenv
from src import pip
from src import webfetch
from src import websearch
from src import tflint
from src import terraform
from src import terragrunt
from src import nslookup
from src import yarn
from src import mkdir
from src import mv
from src import rm
from src import rmdir
from src import cp
from src import cat
from src import git
from src import grep
from src import curl
from src import time
from src import sudo
from src import cd
from src import pwd
from src import bash
from src import ps
from src import pkill
from src import ls
from src import sleep
from src import lsof
from src import kill
from src import kubectl
from src import head
from src import tail
from src import wc
from src import python3
from src import diff
from src import which


def setup_all_policies():
    """Register all policy handlers and middleware with the global registry."""
    registry = get_registry()

    all_middleware = []
    all_middleware.extend(bash.all_middleware)
    all_middleware.extend(time.all_middleware)

    for middleware in all_middleware:
        registry.register_middleware(ToolUseEvent, middleware)

    print(f"Registered {len(all_middleware)} middleware functions successfully!")

    all_rules = []
    all_rules.extend(find.all_rules)
    all_rules.extend(az.all_rules)
    all_rules.extend(python.all_rules)
    all_rules.extend(pytest.all_rules)
    all_rules.extend(virtualenv.all_rules)
    all_rules.extend(pip.all_rules)
    all_rules.extend(webfetch.all_rules)
    all_rules.extend(websearch.all_rules)
    all_rules.extend(tflint.all_rules)
    all_rules.extend(terraform.all_rules)
    all_rules.extend(terragrunt.all_rules)
    all_rules.extend(nslookup.all_rules)
    all_rules.extend(yarn.all_rules)
    all_rules.extend(mkdir.all_rules)
    all_rules.extend(mv.all_rules)
    all_rules.extend(rm.all_rules)
    all_rules.extend(rmdir.all_rules)
    all_rules.extend(cp.all_rules)
    all_rules.extend(cat.all_rules)
    all_rules.extend(git.all_rules)
    all_rules.extend(grep.all_rules)
    all_rules.extend(curl.all_rules)
    all_rules.extend(sudo.all_rules)
    all_rules.extend(pwd.all_rules)
    all_rules.extend(cd.all_rules)
    all_rules.extend(ps.all_rules)
    all_rules.extend(pkill.all_rules)
    all_rules.extend(ls.all_rules)
    all_rules.extend(sleep.all_rules)
    all_rules.extend(lsof.all_rules)
    all_rules.extend(kill.all_rules)
    all_rules.extend(kubectl.all_rules)
    all_rules.extend(head.all_rules)
    all_rules.extend(tail.all_rules)
    all_rules.extend(wc.all_rules)
    all_rules.extend(python3.all_rules)
    all_rules.extend(diff.all_rules)
    all_rules.extend(which.all_rules)

    for rule in all_rules:
        registry.register_handler(ToolUseEvent, rule)

    print(f"Registered {len(all_rules)} policy handlers successfully!")


def main():
    """Start the server with all policies registered."""
    print("Starting AI Agent Policy Server...")

    setup_all_policies()

    print("Server ready with policy enforcement active!")
    print("Starting server on http://localhost:8338")

    uvicorn.run(app, host="0.0.0.0", port=8338, log_level="info")


if __name__ == "__main__":
    main()
