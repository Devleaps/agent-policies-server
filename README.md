# Agent Policies Server

This repository is the public Devleaps policy bundle server: it builds and
serves [OPA](https://www.openpolicyagent.org/) bundles from the Rego policies
in `policies/`. Evaluation happens locally on each developer's machine, in a
stock `opa run --server` daemon managed by the Claude Code plugin - this
server's only job is composing and serving bundles, not evaluating policy
decisions itself.

Client Plugin:
- https://github.com/Devleaps/agent-policies-claude-code

## Quick start

Start the bundle server:
```bash
uv run python -m src.main
```

The server runs on `http://localhost:8338`.

## Architecture

### Bundle composition

`helpers` (path-safety and flag-comparison utilities imported by several
bundles) is a shared Rego dependency. OPA has no supported way to load two
independently-built bundles that each embed a copy of the same package, so
this server composes exactly one bundle per request, containing `helpers`
merged with whichever policy bundles were asked for:

```
GET /bundles/composed?names=universal,python_uv
```

Composed bundles are content-addressed and cached under `bundles/composed/`,
so repeat requests for the same bundle set are free after the first `opa
build`.

### Project structure

```
src/
├── config.py             # host/port settings
├── main.py                # uvicorn entry point
└── server/
    ├── server.py          # FastAPI app, root endpoint
    └── bundles.py          # GET /bundles/composed

policies/
├── helpers/                # Shared dependency (path safety, flag helpers)
├── universal/               # Always-enforced bundle
│   ├── dangerous_commands.rego
│   ├── file_operations.rego
│   ├── git.rego
│   ├── webfetch.rego
│   └── ...
├── python_pip/              # Opt-in: pip-based projects
├── python_uv/                # Opt-in: uv-based projects
└── demo_bundles/, demo_flags/  # Reference examples

rego_tests/                # Native `opa test` coverage (kept separate from
                            # policies/ so test files never ship in a bundle)

tests/
├── corpus/extracted_bash.yaml  # Declarative equivalence corpus consumed by
│                                 agent-policies-claude-code's run-corpus.js
├── test_bundles.py           # Bundle composition/caching/serving
└── test_root.py
```

## Policy examples

### Rego policy structure

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

### Input document structure

Rego policies receive this input (built client-side by
`agent-policies-claude-code`'s `parser.js`/`paths.js`):

```json
{
  "event": {
    "command": "git commit -m 'message'",
    "tool_name": "Bash",
    "workspace_root": "/workspace",
    "enabled_bundles": ["universal"]
  },
  "parsed": {
    "executable": "git",
    "subcommand": "commit",
    "arguments": [],
    "flags": [],
    "options": {"-m": "message"}
  },
  "resolved_paths": {}
}
```

## Testing

```bash
uv run pytest                  # Bundle server tests
opa check policies              # Verify policies compile under stock OPA
opa test policies rego_tests -v # Run native Rego test coverage
```

## Policy bundles

- **Universal**: File operations, git, dangerous commands, cloud CLIs, WebFetch allowlist
- **Python-pip**: Pip install allowlist, Python quality tools
- **Python-uv**: UV package manager, Python quality tools

Clients request bundles via `GET /bundles/composed?names=<comma-separated bundle names>`.

## Documentation

- `docs/writing-rego-policies.md` - Guide to writing Rego policies (predates
  the move to stock OPA evaluation; the Rego syntax guidance still applies,
  but references to `regopy`-specific behavior are stale)
