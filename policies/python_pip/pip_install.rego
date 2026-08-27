package python_pip

# Pip install policies with PyPI age checking.
#
# Age checking uses a client-driven multi-pass protocol: this bundle can't
# reach PyPI itself (policies stay pure, no http.send), so a pip install
# whose package age is unknown yet returns action "incomplete" with a
# `require` array naming what's needed. The client resolves each entry and
# re-queries with the answer folded into input, keyed by package (a command
# only ever names one package, but the wire format supports several so one
# rule shape covers every measurement kind, not just this one).

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

# pip install, single package, nothing looked up yet - ask the client for
# PyPI metadata before deciding.
decisions[decision] if {
	input.parsed.executable == "pip"
	input.parsed.subcommand == "install"
	not input.parsed.options["-r"]
	pkg := input.parsed.arguments[0]
	not input.pypi_lookup_attempted[pkg]
	decision := {
		"action": "incomplete",
		"require": [{"kind": "pypi_metadata", "package": pkg}],
	}
}

# pip install with PyPI age check - allow if package >= 365 days old
decisions[decision] if {
	input.parsed.executable == "pip"
	input.parsed.subcommand == "install"
	not input.parsed.options["-r"]
	pkg := input.parsed.arguments[0]
	input.pypi_metadata[pkg].age_days >= 365
	decision := {"action": "allow"}
}

# pip install with PyPI age check - deny if package < 365 days old
decisions[decision] if {
	input.parsed.executable == "pip"
	input.parsed.subcommand == "install"
	not input.parsed.options["-r"]
	pkg := input.parsed.arguments[0]
	input.pypi_metadata[pkg].age_days < 365
	decision := {
		"action": "deny",
		"reason": sprintf("Package '%v' is only %v days old (first released %v). Policy requires packages to be at least 365 days old for security and stability.", [input.pypi_metadata[pkg].name, input.pypi_metadata[pkg].age_days, input.pypi_metadata[pkg].first_version]),
	}
}

# pip install - deny if the client attempted the PyPI lookup and it
# genuinely came back empty (package not found), as opposed to simply not
# having been looked up yet (that case is the "incomplete" rule above).
decisions[decision] if {
	input.parsed.executable == "pip"
	input.parsed.subcommand == "install"
	not input.parsed.options["-r"]
	pkg := input.parsed.arguments[0]
	input.pypi_lookup_attempted[pkg]
	not input.pypi_metadata[pkg]
	decision := {
		"action": "deny",
		"reason": "Package not found on PyPI. Cannot verify package age for security policy.",
	}
}
