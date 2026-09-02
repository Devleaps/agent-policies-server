package python_pip

# Pass 1: nothing looked up yet, must ask the client for pypi_metadata.
test_pip_install_pass1_incomplete_asks_for_pypi_metadata if {
	decisions[{
		"action": "incomplete",
		"require": [{"kind": "pypi_metadata", "package": "requests"}],
	}] with input as {
		"parsed": {"executable": "pip", "subcommand": "install", "arguments": ["requests"], "options": {}},
		"event": {"command": "pip install requests"},
	}
}

# Pass 2, old package: allow.
test_pip_install_pass2_allow_old_package if {
	decisions[{"action": "allow"}] with input as {
		"parsed": {"executable": "pip", "subcommand": "install", "arguments": ["requests"], "options": {}},
		"event": {"command": "pip install requests"},
		"pypi_lookup_attempted": {"requests": true},
		"pypi_metadata": {"requests": {"age_days": 5000, "name": "requests", "first_version": "0.2.0"}},
	}
}

# Pass 2, young package: deny with the age-check reason.
test_pip_install_pass2_deny_young_package if {
	decisions[{
		"action": "deny",
		"reason": concat("", [
			"Package 'superfresh' is only 10 days old (first released 0.1.0). ",
			"Policy requires packages to be at least 365 days old for security and stability.",
		]),
	}] with input as {
		"parsed": {"executable": "pip", "subcommand": "install", "arguments": ["superfresh"], "options": {}},
		"event": {"command": "pip install superfresh"},
		"pypi_lookup_attempted": {"superfresh": true},
		"pypi_metadata": {"superfresh": {"age_days": 10, "name": "superfresh", "first_version": "0.1.0"}},
	}
}

# Pass 2, lookup attempted but genuinely came back empty: deny with the
# not-found reason, distinct from the pass-1 incomplete case.
test_pip_install_pass2_deny_not_found_after_lookup if {
	decisions[{
		"action": "deny",
		"reason": "Package not found on PyPI. Cannot verify package age for security policy.",
	}] with input as {
		"parsed": {"executable": "pip", "subcommand": "install", "arguments": ["totallyfake123"], "options": {}},
		"event": {"command": "pip install totallyfake123"},
		"pypi_lookup_attempted": {"totallyfake123": true},
	}
}

# A package with no lookup attempted at all must never produce "not found" -
# only "incomplete". Guards against the two rules' conditions overlapping.
test_pip_install_missing_metadata_without_attempt_is_incomplete_not_denied if {
	some_input := {
		"parsed": {"executable": "pip", "subcommand": "install", "arguments": ["somepkg"], "options": {}},
		"event": {"command": "pip install somepkg"},
	}
	decisions[{
		"action": "incomplete",
		"require": [{"kind": "pypi_metadata", "package": "somepkg"}],
	}] with input as some_input
	not decisions[{
		"action": "deny",
		"reason": "Package not found on PyPI. Cannot verify package age for security policy.",
	}] with input as some_input
}

# -r requirements.txt path is untouched by the pypi protocol.
test_pip_install_requirements_txt_allowed_without_lookup if {
	decisions[{"action": "allow"}] with input as {
		"parsed": {"executable": "pip", "subcommand": "install", "arguments": [], "options": {"-r": "requirements.txt"}},
		"event": {"command": "pip install -r requirements.txt"},
	}
}
