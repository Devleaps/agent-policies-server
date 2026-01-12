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
├── core/                      # Core command parsing and evaluation
│   ├── bash_evaluator.py     # Rule evaluation logic
│   ├── command_parser.py     # Bash command parser
│   ├── matchers.py           # Command matchers
│   ├── predicates.py         # Validation predicates
│   └── rule_builder.py       # Fluent API for rules
├── bundles/                   # Policy bundles
│   ├── universal/            # Universal policies (always enforced)
│   │   ├── universal.py      # Core file/system policies
│   │   ├── cloud.py          # Cloud CLI tools (kubectl, terraform, az)
│   │   ├── git.py            # Git command policies
│   │   ├── js.py             # JavaScript/Node.js policies
│   │   ├── network.py        # Network command policies
│   │   └── guidance/         # PostFileEditEvent guidance rules
│   ├── python_pip/           # Python-pip bundle (includes universal + pip policies)
│   └── python_uv/            # Python-uv bundle (includes universal + uv policies)
└── middleware/                # Middleware (currently empty)

tests/
├── core/                      # Core functionality tests
│   ├── test_bash_evaluator.py
│   ├── test_command_parser.py
│   ├── test_fluent_api.py
│   └── test_heredoc_parsing.py
├── bundles/                   # Bundle tests
│   ├── universal/            # Universal bundle tests
│   │   ├── guidance/         # Guidance rule tests
│   │   └── test_*.py
│   ├── python_pip/           # Python-pip bundle tests
│   ├── python_uv/            # Python-uv bundle tests
│   ├── test_combined_bundles.py
│   └── test_complex_scenarios.py
├── conftest.py               # Shared test fixtures
└── helpers.py                # Test helper functions
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

#### 2. Bundle Architecture

Policy bundles are self-contained sets of rules. The `python_pip` and `python_uv` bundles include all universal rules plus bundle-specific rules:

```python
# python_uv bundle includes universal rules + uv-specific rules
from src.bundles.universal import all_bash_rules as universal_bash_rules

all_bash_rules = [
    *universal_bash_rules,  # All universal rules
    *policy.all_rules,      # UV-specific rules
]
```

This ensures that clients selecting a bundle get comprehensive policy coverage without needing to enable multiple bundles.

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

1. **Rules evaluated in registration order** (as defined in `src/main.py`)
2. **All matching rules yield decisions** for the command
3. **Decision precedence**: DENY > ASK > ALLOW
4. **If no rules match**, the evaluator yields ASK for user approval

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

**Default Bundle** (universal policies):
```python
registry.register_handler(ToolUseEvent, universal.bash_rules_bundle_universal, bundle="default")
```

**Specialized Bundles** (include universal + bundle-specific policies):
```python
registry.register_handler(ToolUseEvent, python_pip.bash_rules_bundle_python_pip, bundle="python-pip")
registry.register_handler(ToolUseEvent, python_uv.bash_rules_bundle_python_uv, bundle="python-uv")
```

The `python_pip` and `python_uv` bundles **include all universal rules** plus their specific policies, so clients only need to select one bundle. Clients specify bundles via configuration or command-line flags.

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
from src.bundles import {category}

def setup_all_policies():
    registry = get_registry()
    registry.register_handler(ToolUseEvent, {category}.bash_rules_bundle, bundle="{category}")
```

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
pwd, ps, lsof, which, grep, echo

# Workspace-relative paths only
ls, cat, head, tail, mkdir, cp, touch, mv

# Blocked
sudo, kill, awk, xargs, timeout, time, rm (use trash instead)
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

### Adding New Policy Bundles

1. Create new directory: `src/bundles/new_bundle/`
2. Add `__init__.py` with bundle function export
3. Optionally include universal rules for self-contained bundle:

```python
from src.bundles.universal import all_bash_rules as universal_bash_rules
from src.bundles.new_bundle import policy

all_bash_rules = [
    *universal_bash_rules,  # Include universal rules
    *policy.all_rules,      # Bundle-specific rules
]

def bash_rules_bundle_new_bundle(event: ToolUseEvent):
    """Evaluate event against new bundle rules."""
    yield from evaluate_bash_rules(event, all_bash_rules)
```

4. Register in `src/main.py`:

```python
from src.bundles import new_bundle

def setup_all_policies():
    registry = get_registry()
    registry.register_handler(ToolUseEvent, new_bundle.bash_rules_bundle_new_bundle, bundle="new-bundle")
```

### Code Organization Principles

- **Bundles are self-contained** - Specialized bundles include universal rules plus bundle-specific policies
- **Tests mirror src/ structure** - Test directory organization matches src/ directory structure
- **Block wrapper commands** - Commands like `timeout`, `time`, and `xargs` that can bypass policy controls are blocked
- **Safe paths by default** - File operations require workspace-relative paths (no `..`, `/`, `~`)
- **Security first** - Default to ASK for unmatched commands, require explicit allow rules
