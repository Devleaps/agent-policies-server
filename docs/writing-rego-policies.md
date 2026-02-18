# Writing Rego policies for AI agent policy server

## Overview

This guide explains how to write Rego policies for the AI Agent Policy Server using regopy (embedded Rego interpreter).

## Basic structure

Every policy file follows this pattern:

```rego
package <bundle_name>

import data.helpers

# Comment describing the policy
decisions[decision] if {
    # Conditions that must all be true
    input.parsed.executable == "command"
    input.parsed.subcommand == "subcommand"

    # Policy decision
    decision := {"action": "allow", "reason": null}
}
```

## Policy actions

Policies can return four actions (in order of precedence):

1. **HALT**: Stop execution immediately (highest priority)
2. **DENY**: Block the command
3. **ASK**: Prompt user for approval
4. **ALLOW**: Permit the command (lowest priority)

## Input document structure

Policies receive this input:

```json
{
  "event": {
    "session_id": "abc123",
    "source_client": "claude-code",
    "tool_name": "Bash",
    "tool_is_bash": true,
    "command": "git commit -m 'message'",
    "parameters": {}
  },
  "parsed": {
    "executable": "git",
    "subcommand": "commit",
    "arguments": [],
    "flags": [],
    "options": {"-m": "message"},
    "redirects": [],
    "original": "git commit -m 'message'"
  },
  "session_flags": {
    "ran_tests": true,
    "build_cached": true
  }
}
```

## Common patterns

### 1. Simple allow rule

```rego
# Allow git status
decisions[decision] if {
    input.parsed.executable == "git"
    input.parsed.subcommand == "status"
    decision := {"action": "allow", "reason": null}
}
```

### 2. Simple deny rule

```rego
# Deny sudo commands
decisions[decision] if {
    input.parsed.executable == "sudo"
    decision := {
        "action": "deny",
        "reason": "sudo commands are not allowed for security reasons."
    }
}
```

### 3. Path validation

```rego
import data.helpers

# Allow cat with safe paths
decisions[decision] if {
    input.parsed.executable == "cat"
    count(input.parsed.arguments) > 0
    every arg in input.parsed.arguments {
        helpers.is_safe_path(arg)
    }
    decision := {"action": "allow", "reason": null}
}

# Deny cat with unsafe paths
decisions[decision] if {
    input.parsed.executable == "cat"
    not all_args_safe
    decision := {
        "action": "deny",
        "reason": "Only workspace-relative paths allowed"
    }
}

# Helper
all_args_safe if {
    count(input.parsed.arguments) > 0
    every arg in input.parsed.arguments {
        helpers.is_safe_path(arg)
    }
}
```

### 4. Flag checking

```rego
# Deny git push --force
decisions[decision] if {
    input.parsed.executable == "git"
    input.parsed.subcommand == "push"
    has_force_flag
    decision := {
        "action": "deny",
        "reason": "Force push not allowed"
    }
}

# Helper
has_force_flag if {
    input.parsed.flags[_] == "--force"
}

has_force_flag if {
    input.parsed.flags[_] == "-f"
}
```

### 5. Option checking

Options are key-value pairs like `-m "message"` or `-l file.txt`.

```rego
# Require git commit to have message
decisions[decision] if {
    input.parsed.executable == "git"
    input.parsed.subcommand == "commit"
    has_message
    decision := {"action": "allow", "reason": null}
}

has_message if {
    input.parsed.options["-m"]
}

has_message if {
    input.parsed.options["--message"]
}
```

### 6. Enriched data access

Use enriched external data (like PyPI metadata):

```rego
# Check package age
decisions[decision] if {
    input.parsed.executable == "uv"
    input.parsed.subcommand == "add"
    input.pypi_metadata.age_days < 365
    decision := {
        "action": "deny",
        "reason": sprintf("Package %v is only %v days old",
            [input.pypi_metadata.name, input.pypi_metadata.age_days])
    }
}
```

### 7. Session flags - stateful policies

Session flags enable stateful policy workflows that persist across multiple commands. Flags can expire based on invocation count or time.

#### Basic flag usage

```rego
import data.helpers.flags

# Check if a flag is set (truthy)
decisions[decision] if {
    flags.is_set("flag_name")
    # ... policy logic
}

# Check if a flag has a specific value
decisions[decision] if {
    flags.equals("flag_name", true)
    # ... policy logic
}
```

#### Setting flags

Policies can set flags by including them in decisions:

```rego
# Set a flag that expires after 100 invocations
decisions[decision] if {
    input.parsed.executable == "pytest"
    decision := {
        "action": "allow",
        "flags": [
            {
                "name": "ran_tests",
                "value": true,
                "expires_after": 100,
                "expires_unit": "invocations"
            }
        ]
    }
}

# Set a flag that expires after 60 seconds
decisions[decision] if {
    input.parsed.executable == "docker"
    input.parsed.subcommand == "build"
    decision := {
        "action": "allow",
        "flags": [
            {
                "name": "build_cached",
                "value": true,
                "expires_after": 60,
                "expires_unit": "seconds"
            }
        ]
    }
}
```

#### Pattern 1: Test tracking

Require tests before commits:

```rego
import data.helpers.flags

# Running pytest sets a flag
decisions[decision] if {
    input.parsed.executable == "pytest"
    decision := {
        "action": "allow",
        "flags": [
            {
                "name": "ran_tests",
                "value": true,
                "expires_after": 100,
                "expires_unit": "invocations"
            }
        ]
    }
}

# Commit requires tests
decisions[decision] if {
    input.parsed.executable == "git"
    input.parsed.subcommand == "commit"
    not flags.equals("ran_tests", true)
    decision := {
        "action": "deny",
        "reason": "Please run pytest before committing"
    }
}
```

#### Pattern 2: Cooldown

Show a warning once, then allow for N invocations:

```rego
import data.helpers.flags

# Deny once with warning, then set cooldown
decisions[decision] if {
    input.parsed.executable == "gh"
    input.parsed.subcommand == "pr"
    count(input.parsed.arguments) >= 1
    input.parsed.arguments[0] == "create"
    not flags.is_set("pr_template_cooldown")
    decision := {
        "action": "deny",
        "reason": "Please check .github/PULL_REQUEST_TEMPLATE.md",
        "flags": [
            {
                "name": "pr_template_cooldown",
                "expires_after": 10,
                "expires_unit": "invocations"
            }
        ]
    }
}

# During cooldown, the deny rule doesn't match, so command is allowed
```

#### Pattern 3: Multi-step workflow

Enforce ordered workflow steps (lint → test → deploy):

```rego
import data.helpers.flags

# Step 1: Linting sets a flag
decisions[decision] if {
    input.parsed.executable == "ruff"
    input.parsed.subcommand == "check"
    decision := {
        "action": "allow",
        "flags": [
            {
                "name": "passed_lint",
                "value": true,
                "expires_after": 50,
                "expires_unit": "invocations"
            }
        ]
    }
}

# Step 2: Testing requires lint
decisions[decision] if {
    input.parsed.executable == "pytest"
    not flags.equals("passed_lint", true)
    decision := {
        "action": "deny",
        "reason": "Please run 'ruff check' before running tests"
    }
}

# Step 3: Deploy requires both lint and tests
decisions[decision] if {
    input.parsed.executable == "docker"
    input.parsed.subcommand == "push"
    not flags.equals("passed_lint", true)
    decision := {
        "action": "deny",
        "reason": "Deploy requires lint. Run 'ruff check' first."
    }
}

decisions[decision] if {
    input.parsed.executable == "docker"
    input.parsed.subcommand == "push"
    not flags.equals("passed_tests", true)
    decision := {
        "action": "deny",
        "reason": "Deploy requires tests. Run 'pytest' first."
    }
}
```

#### Pattern 4: Immediate expiration

Flags with `expires_after: 0` expire immediately and are only visible in the same policy evaluation:

```rego
# Set a flag that expires immediately
decisions[decision] if {
    input.parsed.executable == "echo"
    count(input.parsed.arguments) > 0
    input.parsed.arguments[0] == "trigger"
    decision := {
        "action": "allow",
        "flags": [
            {
                "name": "one_time_flag",
                "expires_after": 0,
                "expires_unit": "invocations"
            }
        ]
    }
}

# This rule will never match (flag already expired)
decisions[decision] if {
    flags.is_set("one_time_flag")
    # ... this won't execute
}
```

#### Invalidating flags

Set a flag to `false` to invalidate it:

```rego
# File edit invalidates test flag
decisions[decision] if {
    input.file_path
    endswith(input.file_path, ".py")
    decision := {
        "flags": [
            {
                "name": "ran_tests",
                "value": false
            }
        ]
    }
}
```

#### Flag input structure

Session flags are available in `input.session_flags`:

```json
{
  "session_flags": {
    "ran_tests": true,
    "build_cached": true,
    "passed_lint": true
  }
}
```

## Helper functions

### Available helpers (`data.helpers`)

#### `is_safe_path(path)`
Validates that a path is workspace-relative and safe.

**Blocks:**
- Absolute paths (/etc/passwd)
- Home directory (~)
- Path traversal (../, /..)
- /tmp directory

**Example:**
```rego
import data.helpers

decisions[decision] if {
    input.parsed.executable == "ls"
    count(input.parsed.arguments) > 0
    helpers.is_safe_path(input.parsed.arguments[0])
    decision := {"action": "allow", "reason": null}
}
```

#### `is_localhost_url(URL)`
Validates that a URL is localhost.

**Accepts:**
- localhost, 127.0.0.1, ::1

**Example:**
```rego
import data.helpers

decisions[decision] if {
    input.parsed.executable == "curl"
    count(input.parsed.arguments) > 0
    helpers.is_localhost_url(input.parsed.arguments[0])
    decision := {"action": "allow", "reason": null}
}
```

### Available helpers (`data.helpers.flags`)

#### `flags.is_set(name)`
Check if a session flag exists and has a truthy value.

**Example:**
```rego
import data.helpers.flags

decisions[decision] if {
    flags.is_set("cooldown_active")
    # Flag exists and is truthy
}
```

#### `flags.equals(name, value)`
Check if a session flag exists and has a specific value.

**Example:**
```rego
import data.helpers.flags

decisions[decision] if {
    flags.equals("ran_tests", true)
    # Flag exists and equals true
}
```

## Rego limitations

### 1. No `or` operator in comprehensions

**❌ Don't do this:**
```rego
has_dot_or_slash if {
    chars := split(path, "")
    some char in chars
    char == "." or char == "/"  # ERROR!
}
```

**✅ Do this instead:**
```rego
has_dot if {
    chars := split(path, "")
    some char in chars
    char == "."
}

has_slash if {
    chars := split(path, "")
    some char in chars
    char == "/"
}

has_dot_or_slash if { has_dot }
has_dot_or_slash if { has_slash }
```

### 2. Options vs flags

Commands parse differently:

**Flags** (boolean): `--force`, `-A`
- Stored in: `input.parsed.flags` (array)
- Check with: `input.parsed.flags[_] == "--force"`

**Options** (key-value): `-m "msg"`, `-l file.txt`
- Stored in: `input.parsed.options` (object)
- Check with: `input.parsed.options["-m"]`

**Example:**
```bash
git commit -m "message" --amend
```

Parsed as:
```json
{
  "flags": ["--amend"],
  "options": {"-m": "message"}
}
```

### 3. Arguments vs subcommands

Some commands use subcommands (git, kubectl), others use arguments (yarn).

**Git** (has subcommand):
```bash
git commit -m "msg"
```
```json
{
  "executable": "git",
  "subcommand": "commit",
  "arguments": []
}
```

**Yarn** (no subcommand):
```bash
yarn test
```
```json
{
  "executable": "yarn",
  "subcommand": null,
  "arguments": ["test"]
}
```

## Bundle organization

Policies organize into bundles:

### Universal bundle (`policies/universal/`)
Always enforced for all users.

**Use for:**
- Security policies (sudo, rm, dangerous commands)
- File operation policies
- Git policies
- cloud command-line tool policies

### Python uv bundle (`policies/python_uv/`)
Opt-in bundle for UV-based Python projects.

**Use for:**
- UV-specific policies
- Force tool usage via `uv run`

### Python pip bundle (`policies/python_pip/`)
Opt-in bundle for pip-based Python projects.

**Use for:**
- Direct pip usage allowed
- Direct tool usage allowed (black, pytest, etc.)

## Testing your policies

Create tests in `tests/policies/`:

```python
import pytest
from src.core.rego_integration import RegoEvaluator
from src.core.command_parser import BashCommandParser
from src.server.models import ToolUseEvent, PolicyAction

@pytest.fixture
def rego_evaluator():
    return RegoEvaluator(policy_dir="policies")

@pytest.fixture
def bash_event():
    def _make_event(command: str):
        return ToolUseEvent(
            session_id="test",
            source_client="test",
            tool_name="Bash",
            tool_is_bash=True,
            command=command,
            parameters={}
        )
    return _make_event

def test_my_policy(rego_evaluator, bash_event):
    """Test that my command is allowed."""
    event = bash_event("my-command arg")
    parsed = BashCommandParser.parse("my-command arg")
    
    decisions = rego_evaluator.evaluate(event, parsed, bundles=["universal"])
    
    assert len(decisions) > 0
    assert any(d.action == PolicyAction.ALLOW for d in decisions)
```

## Best practices

1. **One policy file per command category**
   - Example: `git.rego`, `terraform.rego`, `file_operations.rego`

2. **Use descriptive comments**
   - Explain what each rule does
   - Document edge cases

3. **Prefer native Rego over helpers**
   - Only use helpers for complex multi-condition logic
   - Use built-in functions when possible

4. **Test edge cases**
   - Empty arguments
   - Options vs flags
   - Arguments vs subcommands

5. **Clear error messages**
   - Explain why command was denied
   - Suggest alternative command if applicable

6. **Use sprintf for dynamic messages**
   ```rego
   reason := sprintf("Package %v is %v days old", [name, age])
   ```

## Example: Complete policy file

```rego
package universal

import data.helpers

# Sleep command with duration limit
# - Allow if duration <= 60 seconds
# - Deny if duration > 60 seconds

# Deny sleep > 60 seconds
decisions[decision] if {
    input.parsed.executable == "sleep"
    count(input.parsed.arguments) > 0
    duration := to_number(input.parsed.arguments[0])
    duration > 60
    decision := {
        "action": "deny",
        "reason": sprintf("Sleep duration %v exceeds maximum 60 seconds", [duration])
    }
}

# Allow sleep <= 60 seconds
decisions[decision] if {
    input.parsed.executable == "sleep"
    count(input.parsed.arguments) > 0
    duration := to_number(input.parsed.arguments[0])
    duration <= 60
    decision := {"action": "allow", "reason": null}
}
```

## Debugging tips

1. **Check policy compilation**
   - Errors appear in OPA evaluator logs
   - `rego_parse_error` means syntax error

2. **Debug with print statements**
   - Not supported in regopy
   - Instead: Write debug policies that always return decisions

3. **Test parsing first**
   - Use `BashCommandParser.parse()` to see how commands are parsed
   - Print executable, subcommand, arguments, flags, options

4. **Check decision precedence**
   - Remember: HALT > DENY > ASK > ALLOW
   - Multiple rules can match; precedence determines final action

## Resources

- [Rego Language Documentation](https://www.openpolicyagent.org/docs/latest/policy-language/)
- [OPA Built-in Functions](https://www.openpolicyagent.org/docs/latest/policy-reference/)
- Existing policies in `policies/` directory
- Test examples in `tests/policies/`
