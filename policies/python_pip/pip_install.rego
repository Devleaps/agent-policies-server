package python_pip

# Pip install policies with PyPI age checking

# pip audit - allow
decisions[decision] if {
	input.parsed.executable == "pip"
	input.parsed.subcommand == "audit"
	decision := {"action": "allow"}
}

# pip freeze - allow
decisions[decision] if {
	input.parsed.executable == "pip"
	input.parsed.subcommand == "freeze"
	decision := {"action": "allow"}
}

# pip show - allow
decisions[decision] if {
	input.parsed.executable == "pip"
	input.parsed.subcommand == "show"
	decision := {"action": "allow"}
}

# pip uninstall - allow
decisions[decision] if {
	input.parsed.executable == "pip"
	input.parsed.subcommand == "uninstall"
	decision := {"action": "allow"}
}

# pip install -r requirements.txt - allow
decisions[decision] if {
	input.parsed.executable == "pip"
	input.parsed.subcommand == "install"
	input.parsed.options["-r"]
	contains(input.event.command, "requirements.txt")
	decision := {"action": "allow"}
}

# pip install with PyPI age check - allow if package >= 365 days old
decisions[decision] if {
	input.parsed.executable == "pip"
	input.parsed.subcommand == "install"
	not input.parsed.options["-r"]
	input.pypi_metadata.age_days >= 365
	decision := {"action": "allow"}
}

# pip install with PyPI age check - deny if package < 365 days old
decisions[decision] if {
	input.parsed.executable == "pip"
	input.parsed.subcommand == "install"
	not input.parsed.options["-r"]
	input.pypi_metadata.age_days < 365
	decision := {
		"action": "deny",
		"reason": sprintf("Package '%v' is only %v days old (first released %v). Policy requires packages to be at least 365 days old for security and stability.", [input.pypi_metadata.name, input.pypi_metadata.age_days, input.pypi_metadata.first_version]),
	}
}

# pip install - deny if PyPI metadata is missing (package not found)
decisions[decision] if {
	input.parsed.executable == "pip"
	input.parsed.subcommand == "install"
	not input.parsed.options["-r"]
	not input.pypi_metadata
	decision := {
		"action": "deny",
		"reason": "Package not found on PyPI. Cannot verify package age for security policy.",
	}
}
