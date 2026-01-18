package python_pip

# Python tool runners - allow direct usage (not via uv)

# black - allow direct usage
decisions[decision] if {
	input.parsed.executable == "black"
	decision := {"action": "allow"}
}

# mypy - allow direct usage
decisions[decision] if {
	input.parsed.executable == "mypy"
	decision := {"action": "allow"}
}

# ruff check - allow
decisions[decision] if {
	input.parsed.executable == "ruff"
	input.parsed.subcommand == "check"
	decision := {"action": "allow"}
}

# ruff format - allow
decisions[decision] if {
	input.parsed.executable == "ruff"
	input.parsed.subcommand == "format"
	decision := {"action": "allow"}
}

# pytest - allow direct usage
decisions[decision] if {
	input.parsed.executable == "pytest"
	decision := {"action": "allow"}
}
