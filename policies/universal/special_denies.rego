package universal

# Special deny rules for security patterns

# Deny commands starting with absolute paths
decisions[decision] if {
	startswith(input.parsed.original, "/")
	decision := {
		"action": "deny",
		"reason": "Absolute path executables are not allowed.\nUse command names directly (e.g., `pytest`) or relative paths (e.g., `./scripts/run.sh`).",
	}
}

# Deny commands starting with .venv/bin/
decisions[decision] if {
	startswith(input.parsed.original, ".venv/bin/")
	decision := {
		"action": "deny",
		"reason": "Direct execution from `.venv/bin/` is not allowed.\nUse `uv run` to execute tools (e.g., `uv run pytest`).",
	}
}
