# Agent Internal Policies

AI Agent Policy Server that enforces security and safety policies for AI agent tool use.

Built on the `devleaps-agent-policies` framework, this FastAPI-based server intercepts and validates tool use commands (primarily bash commands) before execution using **Rego** policies.

## Quick Start

Start the policy server:
```bash
uv run python -m src.main
```

The server runs on `http://localhost:8338`.

## Architecture

### Rego-Based Policy System

All policies are written in **Rego** and evaluated using regopy (embedded Rego interpreter):

- **Policies**: Located in `policies/` directory, organized by bundle
- **Parser**: Python-based bash command parser (bashlex)
- **Evaluator**: Rego policy evaluator (regopy)
- **Bundles**: Universal (always enforced), python-pip, python-uv (opt-in)

### Project Structure

```
src/
├── bundles_impl.py            # Bundle evaluation functions
├── bundles/                   # Guidance implementations only
│   ├── python_uv/guidance.py
│   └── universal/guidance/
├── core/                      # Parser and evaluator
│   ├── command_parser.py      # Bashlex parser
│   └── rego_integration.py    # Rego evaluator
├── main.py                    # Server entry point
└── utils.py                   # Helper utilities

policies/
├── helpers/
│   └── utils.rego             # Reusable Rego helpers
├── universal/                 # Universal bundle (always enforced)
│   ├── dangerous_commands.rego
│   ├── file_operations.rego
│   ├── git.rego
│   ├── network.rego
│   ├── cloud.rego
│   └── ...
├── python_pip/                # Pip bundle (opt-in)
│   ├── pip_install.rego
│   └── tool_runners.rego
└── python_uv/                 # UV bundle (opt-in)
    ├── uv_commands.rego
    └── tool_runners.rego

tests/
├── core/                      # Parser tests
├── bundles/                   # Policy integration tests
└── test_rego_helpers.py       # Helper function tests
```

## Policy Examples

### Rego Policy Structure

```rego
package universal

# Deny dangerous commands
decisions[decision] if {
    input.parsed.executable == "sudo"
    decision := {
        "action": "deny",
        "reason": "sudo commands are not allowed for security reasons."
    }
}

# Allow safe commands
decisions[decision] if {
    input.parsed.executable == "pwd"
    decision := {"action": "allow"}
}
```

### Input Document Structure

Rego policies receive this input:

```json
{
  "event": {
    "command": "git commit -m 'message'",
    "tool_name": "Bash",
    "session_id": "abc123"
  },
  "parsed": {
    "executable": "git",
    "subcommand": "commit",
    "arguments": [],
    "flags": [],
    "options": {"-m": "message"}
  }
}
```

## Testing

```bash
pytest                       # Run all tests
pytest tests/bundles/        # Run bundle tests only
pytest -k "test_git"         # Run specific tests
```

## Policy Bundles

- **Universal**: File operations, git, dangerous commands, cloud CLIs
- **Python-pip**: Pip install whitelist, Python quality tools
- **Python-uv**: UV package manager, Python quality tools

Clients enable bundles via `--bundle` flags when connecting to the server.

## Documentation

- `docs/writing-rego-policies.md` - Complete guide to writing Rego policies
- `CLAUDE.md` - AI assistant guidance for working with this codebase
