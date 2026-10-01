package python_pip

import data.helpers

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
# The -r file itself must be a workspace requirements file, and nothing else
# may be installed: "requirements.txt" elsewhere in the command (pip install
# -r evil.txt && echo requirements.txt) is not enough. A repeated -r hides
# the earlier file from the parser, so it defers.
pip_requirements_file(path) if {
	helpers.is_safe_path(path)
	regex.match(`(^|/)requirements[A-Za-z0-9_.-]*\.txt$`, path)
}

pip_repeated_requirements if count(regex.find_n(`(^|\s)(-r|--requirement)(\s|=)`, input.parsed.original, -1)) > 1

decisions[decision] if {
	input.parsed.executable == "pip"
	input.parsed.subcommand == "install"
	count(input.parsed.options) == 1
	count(input.parsed.arguments) == 0
	pip_requirements_file(input.parsed.options["-r"])
	not pip_repeated_requirements
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
