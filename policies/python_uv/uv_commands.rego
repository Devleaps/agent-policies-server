# METADATA
# scope: package
# entrypoint: true
package python_uv

import data.helpers

# UV package manager policies

# Direct pip usage denied
decisions contains decision if {
	input.parsed.executable == "pip"
	decision := {
		"action": "deny",
		"reason": concat("", [
			"Direct `pip` usage is not allowed. To add dependencies: use `uv add package-name` (has integrated whitelist). ",
			"To sync existing dependencies: use `uv sync`. Example: `uv add requests`",
		]),
	}
}

# Deny uv run pip
decisions contains decision if {
	input.parsed.executable == "uv"
	input.parsed.subcommand == "run"
	count(input.parsed.arguments) > 0
	input.parsed.arguments[0] == "pip"
	decision := {
		"action": "deny",
		"reason": concat("", [
			"Arbitrary `pip` installation not allowed via `uv run`. ",
			"To add dependencies: use `uv add package-name` (has integrated whitelist). ",
			"To sync existing dependencies: use `uv sync`. Example: `uv add requests`",
		]),
	}
}

# Deny uv pip install specifically
decisions contains decision if {
	input.parsed.executable == "uv"
	input.parsed.subcommand == "pip"
	count(input.parsed.arguments) > 0
	input.parsed.arguments[0] == "install"
	decision := {
		"action": "deny",
		"reason": concat("", [
			"`uv pip install` is not allowed. Use `uv add` instead for better dependency management. ",
			"Example: `uv add package-name`",
		]),
	}
}

# Deny uv run python -c (arbitrary code execution)
decisions contains decision if {
	input.parsed.executable == "uv"
	input.parsed.subcommand == "run"
	count(input.parsed.arguments) > 0
	is_python_executable(input.parsed.arguments[0])
	input.parsed.options["-c"]
	decision := {
		"action": "deny",
		"reason": concat("", [
			"Arbitrary code execution via `uv run python -c` is not allowed for security reasons. ",
			"Place code in a script file or use the existing test framework instead.",
		]),
	}
}

# Deny uv run python -m (use uv run directly with tool name)
decisions contains decision if {
	input.parsed.executable == "uv"
	input.parsed.subcommand == "run"
	count(input.parsed.arguments) > 0
	is_python_executable(input.parsed.arguments[0])
	input.parsed.options["-m"]
	decision := {
		"action": "deny",
		"reason": concat("", [
			"`uv run python -m` is redundant. Use `uv run` directly with the module. ",
			"Example: `uv run python -m pytest` → `uv run pytest`",
		]),
	}
}

# Deny uv run python script.py (redundant)
decisions contains decision if {
	input.parsed.executable == "uv"
	input.parsed.subcommand == "run"
	count(input.parsed.arguments) > 1
	is_python_executable(input.parsed.arguments[0])
	not input.parsed.options["-c"]
	not input.parsed.options["-m"]
	decision := {
		"action": "deny",
		"reason": concat("", [
			"`uv run python` is redundant. Use `uv run` directly with the script. ",
			"Example: `uv run python script.py` → `uv run script.py`",
		]),
	}
}

# Deny python -m venv
decisions contains decision if {
	is_python_executable(input.parsed.executable)
	input.parsed.options["-m"] == "venv"
	decision := {
		"action": "deny",
		"reason": "Direct venv creation not allowed. UV manages environments automatically - use 'uv sync' instead.",
	}
}

# Deny python -m <module>
decisions contains decision if {
	is_python_executable(input.parsed.executable)
	input.parsed.options["-m"] != "venv"
	decision := {
		"action": "deny",
		"reason": "Direct python execution not allowed. Use `uv run` instead. Example: `python -m pytest` → `uv run pytest`",
	}
}

# Deny direct python execution (except scripts/ which falls through to ASK)
decisions contains decision if {
	is_python_executable(input.parsed.executable)
	not input.parsed.options["-m"]
	not contains(input.event.command, "scripts/")
	decision := {
		"action": "deny",
		"reason": concat("", [
			"Direct python execution not allowed. Use `uv run` instead. ",
			"Example: `python script.py` → `uv run script.py` ",
			"Or move scripts to `scripts/` folder for user review.",
		]),
	}
}

# uv add, nothing looked up yet - ask the client for PyPI metadata before
# deciding. See policies/python_pip/pip_install.rego for the full protocol
# explanation (this bundle mirrors it exactly, keyed by the same
# extras-stripped package name).
decisions contains decision if {
	input.parsed.executable == "uv"
	input.parsed.subcommand == "add"
	uv_add_has_only_safe_flags
	not input.pypi_lookup_attempted[uv_add_package_name]
	decision := {
		"action": "incomplete",
		"require": [{"kind": "pypi_metadata", "package": uv_add_package_name}],
	}
}

# Check PyPI package age for uv add
decisions contains decision if {
	input.parsed.executable == "uv"
	input.parsed.subcommand == "add"
	uv_add_has_only_safe_flags
	input.pypi_metadata[uv_add_package_name].age_days < 365
	decision := {
		"action": "deny",
		"reason": sprintf(
			concat("", [
				"Package '%v' is only %v days old (first released %v). ",
				"Policy requires packages to be at least 365 days old for security and stability.",
			]),
			[
				input.pypi_metadata[uv_add_package_name].name,
				input.pypi_metadata[uv_add_package_name].age_days,
				input.pypi_metadata[uv_add_package_name].first_version,
			],
		),
	}
}

# Allow uv add for packages >= 365 days old
decisions contains decision if {
	input.parsed.executable == "uv"
	input.parsed.subcommand == "add"
	uv_add_has_only_safe_flags
	input.pypi_metadata[uv_add_package_name].age_days >= 365
	decision := {"action": "allow"}
}

# Deny uv add if the client attempted the PyPI lookup and it genuinely came
# back empty (package not found), distinct from "not looked up yet".
decisions contains decision if {
	input.parsed.executable == "uv"
	input.parsed.subcommand == "add"
	uv_add_has_only_safe_flags
	input.pypi_lookup_attempted[uv_add_package_name]
	not input.pypi_metadata[uv_add_package_name]
	decision := {
		"action": "deny",
		"reason": "Package not found on PyPI. Cannot verify package age for security policy.",
	}
}

# Deny uv add with unsafe flags
decisions contains decision if {
	input.parsed.executable == "uv"
	input.parsed.subcommand == "add"
	not uv_add_has_only_safe_flags
	decision := {
		"action": "deny",
		"reason": "uv add: unsupported flags detected. Only --dev, -d, --optional, and --group flags are allowed.",
	}
}

# Deny uv run with test file patterns (should use pytest)
decisions contains decision if {
	input.parsed.executable == "uv"
	input.parsed.subcommand == "run"
	decision := {
		"action": "deny",
		"reason": concat("", [
			"Direct execution of test files is not allowed. ",
			"Use `uv run pytest` to run tests with proper test discovery and fixtures. ",
			"Example: `uv run pytest tests/`",
		]),
	}
	some arg in input.parsed.arguments
	contains(arg, "test_")
	endswith(arg, ".py")
}

decisions contains decision if {
	input.parsed.executable == "uv"
	input.parsed.subcommand == "run"
	decision := {
		"action": "deny",
		"reason": concat("", [
			"Direct execution of test files is not allowed. ",
			"Use `uv run pytest` to run tests with proper test discovery and fixtures. ",
			"Example: `uv run pytest tests/`",
		]),
	}
	some arg in input.parsed.arguments
	contains(arg, "_test")
	endswith(arg, ".py")
}

# Allow uv tool install
decisions contains decision if {
	input.parsed.executable == "uv"
	input.parsed.subcommand == "tool"
	count(input.parsed.arguments) > 0
	input.parsed.arguments[0] == "install"
	decision := {"action": "allow"}
}

# Allow uv sync
decisions contains decision if {
	input.parsed.executable == "uv"
	input.parsed.subcommand == "sync"
	decision := {"action": "allow"}
}

# Allow uv remove
decisions contains decision if {
	input.parsed.executable == "uv"
	input.parsed.subcommand == "remove"
	decision := {"action": "allow"}
}

# Deny uv run pytest with unsafe paths
decisions contains decision if {
	input.parsed.executable == "uv"
	input.parsed.subcommand == "run"
	count(input.parsed.arguments) > 1
	input.parsed.arguments[0] == "pytest"
	decision := {
		"action": "deny",
		"reason": concat("", [
			"pytest with unsafe paths is not allowed. ",
			"Use workspace-relative paths only (no absolute paths, no ../, no /tmp).",
		]),
	}
	some arg in input.parsed.arguments
	not helpers.is_safe_path(arg)
}

# Allow whitelisted uv run tools
decisions contains decision if {
	input.parsed.executable == "uv"
	input.parsed.subcommand == "run"
	count(input.parsed.arguments) > 0
	decision := {"action": "allow"}
	some tool in uv_run_allowed_tools
	input.parsed.arguments[0] == tool
}

# Helper to check if argument is python executable
is_python_executable("python")

is_python_executable(arg) if {
	startswith(arg, "python3")
}

# Allowed uv add flags (don't affect package validation)
uv_add_safe_flags := ["--dev", "-d", "--optional", "--group"]

# The package name for `uv add`, mirroring the deleted _enrich_input's
# extraction order exactly: first non-flag positional argument, falling back
# to the value of --dev/-d/--group/--optional if no positional argument
# exists (e.g. `uv add --dev pytest-cov` has no positional argument at all -
# the parser puts pytest-cov in options["--dev"]). Extras are NOT stripped
# here; that happens once, in the client, before it looks the package up.
uv_add_raw_package_name := input.parsed.arguments[0] if {
	count(input.parsed.arguments) > 0
} else := input.parsed.options["--dev"] if {
	input.parsed.options["--dev"]
} else := input.parsed.options["-d"] if {
	input.parsed.options["-d"]
} else := input.parsed.options["--group"] if {
	input.parsed.options["--group"]
} else := input.parsed.options["--optional"] if {
	input.parsed.options["--optional"]
}

# Strip extras, e.g. "uvicorn[standard]" -> "uvicorn" - this is the PyPI
# lookup key, matching the deleted _enrich_input's base_name computation.
uv_add_package_name := split(uv_add_raw_package_name, "[")[0]

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

# Whitelisted tools allowed
uv_run_allowed_tools := ["black", "ruff", "mypy", "pytest"]
