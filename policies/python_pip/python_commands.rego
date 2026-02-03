package python_pip

# Python execution policies for pip-based projects

# Helper to check if executable is python
is_python_exec if {
	input.parsed.executable == "python"
}

is_python_exec if {
	startswith(input.parsed.executable, "python3")
}

# python -m venv - deny
decisions[decision] if {
	is_python_exec
	input.parsed.options["-m"] == "venv"
	decision := {
		"action": "deny",
		"reason": "By policy, `python -m venv` is not allowed. Use `uv sync` for virtual environment management.",
	}
}

# python -c - deny
decisions[decision] if {
	is_python_exec
	input.parsed.options["-c"]
	decision := {
		"action": "deny",
		"reason": "By policy, python -c commands are not allowed. For scripts, place them in a directory and run with python. To test new functionality: add test cases and run with `pytest`. Quick verification scripts are discouraged - use the existing test framework instead.",
	}
}

# python -m pytest - deny (use pytest directly)
decisions[decision] if {
	is_python_exec
	input.parsed.options["-m"] == "pytest"
	decision := {
		"action": "deny",
		"reason": "By policy, `python -m pytest` have been disallowed. Use `pytest` directly.",
	}
}

# python test_*.py - deny (use pytest)
decisions[decision] if {
	is_python_exec
	count(input.parsed.arguments) > 0
	startswith(input.parsed.arguments[0], "test_")
	endswith(input.parsed.arguments[0], ".py")
	decision := {
		"action": "deny",
		"reason": "By policy, direct execution of test files is not allowed. Use `pytest` to run tests.",
	}
}
