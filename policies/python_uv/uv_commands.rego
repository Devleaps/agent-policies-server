package python_uv

# UV package manager policies

# Direct pip usage denied
decisions[decision] if {
	input.parsed.executable == "pip"
	decision := {
		"action": "deny",
		"reason": "Direct `pip` usage is not allowed.\\nTo add dependencies: use `uv add package-name` (has integrated whitelist).\\nTo sync existing dependencies: use `uv sync`.\\nExample: `uv add requests`",
	}
}

# Deny uv run pip
decisions[decision] if {
	input.parsed.executable == "uv"
	input.parsed.subcommand == "run"
	count(input.parsed.arguments) > 0
	input.parsed.arguments[0] == "pip"
	decision := {
		"action": "deny",
		"reason": "Arbitrary `pip` installation not allowed via `uv run`.\\nTo add dependencies: use `uv add package-name` (has integrated whitelist).\\nTo sync existing dependencies: use `uv sync`.\\nExample: `uv add requests`",
	}
}

# Deny uv pip install specifically
decisions[decision] if {
	input.parsed.executable == "uv"
	input.parsed.subcommand == "pip"
	count(input.parsed.arguments) > 0
	input.parsed.arguments[0] == "install"
	decision := {
		"action": "deny",
		"reason": "`uv pip install` is not allowed. Use `uv add` instead for better dependency management.\\nExample: `uv add package-name`",
	}
}

# Helper to check if argument is python executable
is_python_executable(arg) if {
	arg == "python"
}

is_python_executable(arg) if {
	startswith(arg, "python3")
}

# Deny uv run python -c (arbitrary code execution)
decisions[decision] if {
	input.parsed.executable == "uv"
	input.parsed.subcommand == "run"
	count(input.parsed.arguments) > 0
	is_python_executable(input.parsed.arguments[0])
	input.parsed.options["-c"]
	decision := {
		"action": "deny",
		"reason": "Arbitrary code execution via `uv run python -c` is not allowed for security reasons.\\nPlace code in a script file or use the existing test framework instead.",
	}
}

# Deny uv run python -m (use uv run directly with tool name)
decisions[decision] if {
	input.parsed.executable == "uv"
	input.parsed.subcommand == "run"
	count(input.parsed.arguments) > 0
	is_python_executable(input.parsed.arguments[0])
	input.parsed.options["-m"]
	decision := {
		"action": "deny",
		"reason": "`uv run python -m` is redundant. Use `uv run` directly with the module.\\nExample: `uv run python -m pytest` → `uv run pytest`",
	}
}

# Deny uv run python script.py (redundant)
decisions[decision] if {
	input.parsed.executable == "uv"
	input.parsed.subcommand == "run"
	count(input.parsed.arguments) > 1
	is_python_executable(input.parsed.arguments[0])
	not input.parsed.options["-c"]
	not input.parsed.options["-m"]
	decision := {
		"action": "deny",
		"reason": "`uv run python` is redundant. Use `uv run` directly with the script.\\nExample: `uv run python script.py` → `uv run script.py`",
	}
}

# Deny python -m venv
decisions[decision] if {
	is_python_executable(input.parsed.executable)
	input.parsed.options["-m"] == "venv"
	decision := {
		"action": "deny",
		"reason": "Direct venv creation not allowed.\\nUV manages environments automatically - use 'uv sync' instead.",
	}
}

# Deny python -m <module>
decisions[decision] if {
	is_python_executable(input.parsed.executable)
	input.parsed.options["-m"]
	input.parsed.options["-m"] != "venv"
	decision := {
		"action": "deny",
		"reason": "Direct python execution not allowed. Use `uv run` instead.\\nExample: `python -m pytest` → `uv run pytest`",
	}
}

# Deny direct python execution (except scripts/ which falls through to ASK)
decisions[decision] if {
	is_python_executable(input.parsed.executable)
	not input.parsed.options["-m"]
	not contains(input.event.command, "scripts/")
	decision := {
		"action": "deny",
		"reason": "Direct python execution not allowed. Use `uv run` instead.\\nExample: `python script.py` → `uv run script.py`\\nOr move scripts to `scripts/` folder for user review.",
	}
}

# Check PyPI package age for uv add
decisions[decision] if {
	input.parsed.executable == "uv"
	input.parsed.subcommand == "add"
	input.pypi_metadata.age_days < 365
	decision := {
		"action": "deny",
		"reason": sprintf("Package '%v' is only %v days old (first released %v). Policy requires packages to be at least 365 days old for security and stability.", [input.pypi_metadata.name, input.pypi_metadata.age_days, input.pypi_metadata.first_version]),
	}
}

# Allow uv add for packages >= 365 days old
decisions[decision] if {
	input.parsed.executable == "uv"
	input.parsed.subcommand == "add"
	input.pypi_metadata.age_days >= 365
	decision := {
		"action": "allow",
	}
}

# Deny uv add if PyPI metadata is missing (package not found)
decisions[decision] if {
	input.parsed.executable == "uv"
	input.parsed.subcommand == "add"
	not input.pypi_metadata
	decision := {
		"action": "deny",
		"reason": "Package not found on PyPI. Cannot verify package age for security policy.",
	}
}

# Allow uv sync
decisions[decision] if {
	input.parsed.executable == "uv"
	input.parsed.subcommand == "sync"
	decision := {
		"action": "allow",
	}
}

# Allow uv run with tool runners (black, ruff, mypy, pytest)
decisions[decision] if {
	input.parsed.executable == "uv"
	input.parsed.subcommand == "run"
	count(input.parsed.arguments) > 0
	input.parsed.arguments[0] == "black"
	decision := {
		"action": "allow",
	}
}

decisions[decision] if {
	input.parsed.executable == "uv"
	input.parsed.subcommand == "run"
	count(input.parsed.arguments) > 0
	input.parsed.arguments[0] == "ruff"
	decision := {
		"action": "allow",
	}
}

decisions[decision] if {
	input.parsed.executable == "uv"
	input.parsed.subcommand == "run"
	count(input.parsed.arguments) > 0
	input.parsed.arguments[0] == "mypy"
	decision := {
		"action": "allow",
	}
}

decisions[decision] if {
	input.parsed.executable == "uv"
	input.parsed.subcommand == "run"
	count(input.parsed.arguments) > 0
	input.parsed.arguments[0] == "pytest"
	decision := {
		"action": "allow",
	}
}

# Allow other uv run commands (scripts, etc.)
decisions[decision] if {
	input.parsed.executable == "uv"
	input.parsed.subcommand == "run"
	count(input.parsed.arguments) > 0
	input.parsed.arguments[0] != "pip"
	not is_python_executable(input.parsed.arguments[0])
	input.parsed.arguments[0] != "black"
	input.parsed.arguments[0] != "ruff"
	input.parsed.arguments[0] != "mypy"
	input.parsed.arguments[0] != "pytest"
	decision := {
		"action": "allow",
	}
}
