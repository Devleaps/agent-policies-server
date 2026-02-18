package python_uv

import data.helpers

# UV package manager policies

# Direct pip usage denied
decisions[decision] if {
	input.parsed.executable == "pip"
	decision := {
		"action": "deny",
		"reason": "Direct `pip` usage is not allowed. To add dependencies: use `uv add package-name` (has integrated whitelist). To sync existing dependencies: use `uv sync`. Example: `uv add requests`",
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
		"reason": "Arbitrary `pip` installation not allowed via `uv run`. To add dependencies: use `uv add package-name` (has integrated whitelist). To sync existing dependencies: use `uv sync`. Example: `uv add requests`",
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
		"reason": "`uv pip install` is not allowed. Use `uv add` instead for better dependency management. Example: `uv add package-name`",
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
		"reason": "Arbitrary code execution via `uv run python -c` is not allowed for security reasons. Place code in a script file or use the existing test framework instead.",
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
		"reason": "`uv run python -m` is redundant. Use `uv run` directly with the module. Example: `uv run python -m pytest` → `uv run pytest`",
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
		"reason": "`uv run python` is redundant. Use `uv run` directly with the script. Example: `uv run python script.py` → `uv run script.py`",
	}
}

# Deny python -m venv
decisions[decision] if {
	is_python_executable(input.parsed.executable)
	input.parsed.options["-m"] == "venv"
	decision := {
		"action": "deny",
		"reason": "Direct venv creation not allowed. UV manages environments automatically - use 'uv sync' instead.",
	}
}

# Deny python -m <module>
decisions[decision] if {
	is_python_executable(input.parsed.executable)
	input.parsed.options["-m"]
	input.parsed.options["-m"] != "venv"
	decision := {
		"action": "deny",
		"reason": "Direct python execution not allowed. Use `uv run` instead. Example: `python -m pytest` → `uv run pytest`",
	}
}

# Deny direct python execution (except scripts/ which falls through to ASK)
decisions[decision] if {
	is_python_executable(input.parsed.executable)
	not input.parsed.options["-m"]
	not contains(input.event.command, "scripts/")
	decision := {
		"action": "deny",
		"reason": "Direct python execution not allowed. Use `uv run` instead. Example: `python script.py` → `uv run script.py` Or move scripts to `scripts/` folder for user review.",
	}
}

# Allowed uv add flags (don't affect package validation)
uv_add_safe_flags := ["--dev", "-d", "--optional", "--group"]

# Check if all flags are safe for uv add
uv_add_has_only_safe_flags if {
	count(input.parsed.flags) == 0
}

uv_add_has_only_safe_flags if {
	count(input.parsed.flags) > 0
	every flag in input.parsed.flags {
		flag in uv_add_safe_flags
	}
}

# Check PyPI package age for uv add
decisions[decision] if {
	input.parsed.executable == "uv"
	input.parsed.subcommand == "add"
	uv_add_has_only_safe_flags
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
	uv_add_has_only_safe_flags
	input.pypi_metadata.age_days >= 365
	decision := {"action": "allow"}
}

# Deny uv add if PyPI metadata is missing (package not found)
decisions[decision] if {
	input.parsed.executable == "uv"
	input.parsed.subcommand == "add"
	uv_add_has_only_safe_flags
	not input.pypi_metadata
	decision := {
		"action": "deny",
		"reason": "Package not found on PyPI. Cannot verify package age for security policy.",
	}
}

# Deny uv add with unsafe flags
decisions[decision] if {
	input.parsed.executable == "uv"
	input.parsed.subcommand == "add"
	not uv_add_has_only_safe_flags
	decision := {
		"action": "deny",
		"reason": "uv add: unsupported flags detected. Only --dev, -d, --optional, and --group flags are allowed.",
	}
}

# Deny uv run with test file patterns (should use pytest)
decisions[decision] if {
	input.parsed.executable == "uv"
	input.parsed.subcommand == "run"
	count(input.parsed.arguments) > 0
	some arg in input.parsed.arguments
	contains(arg, "test_")
	endswith(arg, ".py")
	decision := {
		"action": "deny",
		"reason": "Direct execution of test files is not allowed. Use `uv run pytest` to run tests with proper test discovery and fixtures. Example: `uv run pytest tests/`",
	}
}

decisions[decision] if {
	input.parsed.executable == "uv"
	input.parsed.subcommand == "run"
	count(input.parsed.arguments) > 0
	some arg in input.parsed.arguments
	contains(arg, "_test")
	endswith(arg, ".py")
	decision := {
		"action": "deny",
		"reason": "Direct execution of test files is not allowed. Use `uv run pytest` to run tests with proper test discovery and fixtures. Example: `uv run pytest tests/`",
	}
}

# Allow uv sync
decisions[decision] if {
	input.parsed.executable == "uv"
	input.parsed.subcommand == "sync"
	decision := {"action": "allow"}
}

# Allow uv remove
decisions[decision] if {
	input.parsed.executable == "uv"
	input.parsed.subcommand == "remove"
	decision := {"action": "allow"}
}

# Whitelisted tools allowed
uv_run_allowed_tools := ["black", "ruff", "mypy", "pytest"]

# Deny uv run pytest with unsafe paths
decisions[decision] if {
	input.parsed.executable == "uv"
	input.parsed.subcommand == "run"
	count(input.parsed.arguments) > 1
	input.parsed.arguments[0] == "pytest"
	some arg in input.parsed.arguments
	not helpers.is_safe_path(arg)
	decision := {
		"action": "deny",
		"reason": "pytest with unsafe paths is not allowed. Use workspace-relative paths only (no absolute paths, no ../, no /tmp).",
	}
}

# Allow whitelisted uv run tools
decisions[decision] if {
	input.parsed.executable == "uv"
	input.parsed.subcommand == "run"
	count(input.parsed.arguments) > 0
	some tool in uv_run_allowed_tools
	input.parsed.arguments[0] == tool
	decision := {"action": "allow"}
}
