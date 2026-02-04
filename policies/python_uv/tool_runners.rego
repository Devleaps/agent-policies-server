package python_uv

# Tool runner policies - force usage via uv run

# Deny direct black usage
decisions[decision] if {
	input.parsed.executable == "black"
	decision := {
		"action": "deny",
		"reason": "Black must be run via uv. Use: uv run black .",
	}
}

# Deny direct ruff usage
decisions[decision] if {
	input.parsed.executable == "ruff"
	decision := {
		"action": "deny",
		"reason": "Ruff must be run via uv. Use: uv run ruff check . OR uv run ruff format .",
	}
}

# Deny direct mypy usage
decisions[decision] if {
	input.parsed.executable == "mypy"
	decision := {
		"action": "deny",
		"reason": "Mypy must be run via uv. Use: uv run mypy .",
	}
}

# Deny direct pytest usage
decisions[decision] if {
	input.parsed.executable == "pytest"
	decision := {
		"action": "deny",
		"reason": "Pytest must be run via uv. Use: uv run pytest",
	}
}
