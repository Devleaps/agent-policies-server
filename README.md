# AI Agent Policy Server

A FastAPI-based policy enforcement server that validates AI agent tool use commands before execution. Built on the `devleaps-agent-policies` framework, this server intercepts and evaluates tool use events (primarily bash commands) against comprehensive security and safety policies.

## Overview

This policy server acts as a security layer for AI agent operations, enforcing rules around:

- **File operations** (rm, mv, cp, mkdir, etc.)
- **Git commands** (commit, push, add, etc.)
- **Package management** (pip, uv)
- **Cloud tools** (kubectl, terraform, az)
- **Network operations** (curl, web requests)
- **Code quality** (comment ratios, import placement, legacy code patterns)

The server runs on `http://localhost:8338` and returns policy decisions (`allow`, `deny`, `ask`, `halt`) or guidance for each operation.

## Quick Start

### Installation

```bash
# Install dependencies
uv sync
```

### Running the Server

```bash
# Using the convenience script
./bin/internal-policy-server

# Or directly
uv run python -m src.main
```

The server will start on `http://localhost:8338` with all policies active.

### Running with Docker

```bash
docker build -t agent-policy-server .
docker run -p 8338:8338 agent-policy-server
```

## Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_git_commit_m_flag.py

# Verbose output
pytest -v

# Run tests matching pattern
pytest -k "test_name"
```

**Important**: Use `pytest` directly, not `python -m pytest`.

## Architecture

### Project Structure

```
src/
├── main.py                    # Server entry point and policy registration
├── utils.py                   # PolicyHelper and security utilities
├── universal/                 # Universal file/system policies
│   ├── whitelist_always.py   # Always-allowed commands
│   ├── whitelist_safe_paths.py  # Safe-path commands
│   ├── bash_middleware.py    # Command splitting (&&, |)
│   ├── *_middleware.py       # Other middleware
│   └── *.py                  # Individual command policies
├── git/                      # Git command policies
├── cloud/                    # Cloud CLI tools (kubectl, terraform, az)
├── network/                  # Network command policies
├── python/                   # Python shared policies
│   └── *_guidance.py         # PostFileEditEvent guidance rules
├── js/                       # JavaScript/Node.js policies
├── python_pip/               # Python-pip bundle (opt-in)
└── python_uv/                # Python-uv bundle (opt-in)

tests/
└── test_*.py                 # Test files
```

### Core Components

#### 1. Policy Rules

Each policy rule is a generator function that yields `PolicyDecision` or `PolicyGuidance`:

```python
def rule_name(input_data: ToolUseEvent):
    """Rule description."""
    if not input_data.tool_is_bash:
        return

    if re.match(r'pattern', input_data.command):
        yield PolicyHelper.allow()
        return

    return None  # No opinion - other rules may handle it
```

**Policy Decision Types**:
- `allow()` - Permit the operation
- `deny(reason)` - Block the operation with explanation
- `ask()` - Prompt user for approval
- `halt()` - Stop entire process
- `guidance(content)` - Provide non-blocking advice

#### 2. Middleware

Middleware preprocesses tool use events before policy evaluation:

```python
def middleware_function(input_data: ToolUseEvent):
    """Transform or split commands before policy evaluation."""
    # Can yield multiple events from one input
    if '&&' in input_data.command:
        # Split into separate events
        for cmd in commands:
            yield ToolUseEvent(...)
    else:
        yield input_data
```

Examples: command splitting (`cmd1 && cmd2`), stripping time/timeout prefixes.

#### 3. Event Types

- **ToolUseEvent**: Before tool execution (bash commands, etc.)
- **PostToolUseEvent**: After tool execution
- **FileEditEvent**: Before file edits
- **PostFileEditEvent**: After file edits (guidance only)

#### 4. Policy Helper Utilities

The `PolicyHelper` class provides convenient methods for creating policy decisions:

```python
from src.utils import PolicyHelper

# Allow operation
yield PolicyHelper.allow()

# Deny with reason
yield PolicyHelper.deny("Operation not permitted because...")

# Ask user for approval
yield PolicyHelper.ask()

# Stop entire process
yield PolicyHelper.halt()

# Provide guidance without blocking
yield PolicyHelper.guidance("Consider using X instead of Y")
```

**Security Utilities**:
- `path_appears_safe(path)` - Validates paths for safety (no `..`, `/tmp/`, absolute paths)
- `path_in_command_appears_safe(command, cmd_name)` - Extracts and validates paths from commands
- `url_is_localhost(url)` - Checks if URL points to localhost

### Rule Evaluation Flow

1. **Middleware runs first** and can transform/split events
2. **Rules evaluated in registration order** (as defined in `src/main.py`)
3. **First rule that yields a decision wins**
4. **If no rules yield a decision**, default policy applies (typically deny)

### Policy Organization Patterns

#### Simple Whitelists

Commands are organized into two main whitelists:

**Always Allowed Commands** (`universal/whitelist_always.py`):
- Commands allowed with any parameters
- Examples: `pwd`, `ps`, `lsof`, `which`, `grep`, `pytest`

**Safe Path Commands** (`universal/whitelist_safe_paths.py`):
- Commands allowed with workspace-relative paths only
- Examples: `ls`, `cat`, `head`, `tail`, `mkdir`, `cp`, `touch`
- Blocks absolute paths, `..` traversal, and `/tmp/` operations

#### Complex Policies

Individual files for commands requiring special logic:
- `sleep_allow.py` - Limits sleep duration to ≤60 seconds
- `sqlite3_allow.py` - Only allows SELECT queries, blocks writes
- `pip_install_whitelist.py` - Enforces package whitelist
- `git_policy.py` - Requires `-m` flag for commits, blocks unsafe operations

### Universal vs. Bundle Policies

**Universal Policies** (always enforced):
```python
registry.register_all_handlers(ToolUseEvent, universal.all_rules)
registry.register_all_handlers(ToolUseEvent, git.all_rules)
```

**Bundle Policies** (opt-in by client):
```python
registry.register_all_handlers(ToolUseEvent, python_pip.all_rules, bundle="python-pip")
registry.register_all_handlers(ToolUseEvent, python_uv.all_rules, bundle="python-uv")
```

Clients enable bundles via `--bundle python-pip` or `--bundle python-uv` flags.

### Session State Management

Server-side session state storage for stateful policy enforcement:

```python
from devleaps.policies.server.session import get_session_state, set_session_flag

# Store session-specific data
set_session_flag(session_id, "key", value)

# Retrieve session data
value = get_session_flag(session_id, "key")
```

Use cases: tracking user consent, feature flags, multi-step workflows.

## Adding New Policies

### Option 1: Add to Whitelist (Simple Commands)

For commands that should always be allowed or require only path safety checks:

**Always allowed** (`src/universal/whitelist_always.py`):
```python
ALWAYS_ALLOWED_COMMANDS = [
    "pwd",
    "ps",
    # ... existing commands ...
    "your_command",  # Add here
]
```

**Safe paths only** (`src/universal/whitelist_safe_paths.py`):
```python
SAFE_PATH_COMMANDS = [
    "ls",
    "cat",
    # ... existing commands ...
    "your_command",  # Add here
]
```

### Option 2: Create Custom Policy (Complex Logic)

For commands requiring conditional logic, validation, or special handling:

1. **Create policy file**: `src/{category}/your_command.py`

```python
"""Policy for your_command."""

import re
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper

def your_command_rule(input_data: ToolUseEvent):
    """Enforce rules for your_command."""
    if not input_data.tool_is_bash:
        return

    if not input_data.command.strip().startswith('your_command'):
        return

    # Your validation logic here
    if some_condition:
        yield PolicyHelper.deny("Reason for denial")
        return

    yield PolicyHelper.allow()
```

2. **Export in `__init__.py`**: `src/{category}/__init__.py`

```python
from src.{category}.your_command import your_command_rule

all_rules = [
    # ... existing rules ...
    your_command_rule,
]
```

3. **Register in main**: `src/main.py`

```python
from src import {category}

def setup_all_policies():
    registry = get_registry()
    registry.register_all_handlers(ToolUseEvent, {category}.all_rules)
```

### Option 3: Add Middleware

For transforming commands before policy evaluation:

1. **Create middleware file**: `src/{category}/your_middleware.py`

```python
"""Middleware for transforming commands."""

from devleaps.policies.server.common.models import ToolUseEvent

def your_middleware(input_data: ToolUseEvent):
    """Transform commands before policy evaluation."""
    if not input_data.tool_is_bash:
        yield input_data
        return

    # Transform or split commands
    if '&&' in input_data.command:
        for cmd in input_data.command.split('&&'):
            yield ToolUseEvent(
                session_id=input_data.session_id,
                source_client=input_data.source_client,
                tool_name=input_data.tool_name,
                tool_is_bash=True,
                command=cmd.strip(),
                parameters={"command": cmd.strip()}
            )
    else:
        yield input_data
```

2. **Register middleware**: Update `src/{category}/__init__.py` and `src/main.py`

## Writing Tests

Tests follow a standard pattern:

```python
import pytest
from devleaps.policies.server.common.models import ToolUseEvent
from devleaps.policies.server.common.enums import SourceClient
from src.category.your_command import your_command_rule


@pytest.fixture
def create_tool_use_event():
    """Factory fixture to create ToolUseEvent."""
    def _create(command: str, tool_is_bash: bool = True) -> ToolUseEvent:
        return ToolUseEvent(
            session_id="test-session",
            source_client=SourceClient.CLAUDE_CODE,
            tool_name="Bash" if tool_is_bash else "Read",
            tool_is_bash=tool_is_bash,
            command=command,
            parameters={"command": command}
        )
    return _create


def test_your_command_allowed(create_tool_use_event):
    """Test that valid command is allowed."""
    event = create_tool_use_event('your_command arg')
    results = list(your_command_rule(event))
    assert len(results) == 1
    assert results[0].action == "allow"


def test_your_command_denied(create_tool_use_event):
    """Test that invalid command is denied."""
    event = create_tool_use_event('your_command --bad-flag')
    results = list(your_command_rule(event))
    assert len(results) == 1
    assert results[0].action == "deny"
    assert "reason text" in results[0].reason
```

**Key points**:
1. Use `create_tool_use_event()` fixture factory to generate test events
2. Convert generator result to list: `results = list(rule_function(event))`
3. Assert on `results[0].action` (values: `"allow"`, `"deny"`, `"ask"`, `"halt"`)
4. Assert on `results[0].reason` for deny/ask actions

## Policy Examples

### File Operations

```python
# Always allowed
pwd, ps, lsof, which, grep

# Workspace-relative paths only
ls, cat, head, tail, mkdir, cp, touch

# Blocked
sudo, kill, awk, rm (use trash instead)
```

### Git Commands

```python
# Always allowed
git status, git diff, git log, git show

# Requires -m flag
git commit -m "message"

# Allowed with flags
git commit --amend --no-edit

# Blocked
git rm (use trash instead)
git push --force
```

### Python Package Management

**Allowed packages** (defined in `src/python/__init__.py`):
```python
ALLOWED_PACKAGES = {
    "requests", "fastapi", "uvicorn", "pydantic", "pytest",
    "httpx", "fire", "jinja2", "streamlit", "pandas",
    "numpy", "sqlalchemy", "python-dotenv", "pyyaml", "toml"
}
```

### Network Operations

```python
# Only localhost allowed by default
curl localhost:8080
curl 127.0.0.1:3000

# External URLs blocked without approval
```

### Code Quality Guidance

**PostFileEditEvent** rules provide non-blocking guidance:

- **Comment ratio** - Warns if comments exceed 40% of code
- **Comment overlap** - Detects copy-pasted docstrings
- **Mid-code imports** - Flags imports inside function bodies
- **Legacy code patterns** - Detects backwards compatibility code

## Configuration

The server uses environment variables and the `devleaps-agent-policies` framework configuration. Session state is stored in-memory and cleared on restart.

## Dependencies

- **devleaps-agent-policies** - Core policy framework (local editable install)
- **FastAPI** - Web framework
- **uvicorn** - ASGI server
- **pydantic** - Data validation
- **pytest** - Testing framework

## Development

### Running Locally

```bash
# Start server with auto-reload
uv run python -m src.main

# In another terminal, send test requests to http://localhost:8338
```

### Adding New Policy Categories

1. Create new directory: `src/new_category/`
2. Add `__init__.py` with `all_rules = []` export
3. Implement policy rules in separate files
4. Register in `src/main.py`:

```python
from src import new_category

def setup_all_policies():
    registry = get_registry()
    registry.register_all_handlers(ToolUseEvent, new_category.all_rules)
```

### Code Organization Principles

- **Keep whitelists centralized** - Add simple commands to existing whitelist files
- **One file per complex policy** - Commands with special logic get their own file
- **Middleware for transformations** - Use middleware to normalize/split commands
- **Tests mirror implementation** - Test file names match policy file names
- **Security first** - Default to deny, require explicit allow rules
