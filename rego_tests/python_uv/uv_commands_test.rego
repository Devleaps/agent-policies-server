package python_uv

# Package-name extraction, mirroring the deleted _enrich_input exactly.

test_uv_add_package_name_from_argument if {
	uv_add_raw_package_name == "fastapi" with input as {"parsed": {"arguments": ["fastapi"], "options": {}}}
}

test_uv_add_package_name_falls_back_to_dev_option if {
	uv_add_raw_package_name == "pytest-cov" with input as {"parsed": {"arguments": [], "options": {"--dev": "pytest-cov"}}}
}

test_uv_add_package_name_strips_extras if {
	uv_add_package_name == "uvicorn" with input as {"parsed": {"arguments": ["uvicorn[standard]"], "options": {}}}
}

# Incomplete / age-check protocol, same shape as pip_install_test.rego.

test_uv_add_pass1_incomplete_asks_for_pypi_metadata if {
	decisions[{
		"action": "incomplete",
		"require": [{"kind": "pypi_metadata", "package": "fastapi"}],
	}] with input as {"parsed": {"executable": "uv", "subcommand": "add", "arguments": ["fastapi"], "flags": [], "options": {}}}
}

test_uv_add_pass1_incomplete_strips_extras_in_require if {
	decisions[{
		"action": "incomplete",
		"require": [{"kind": "pypi_metadata", "package": "uvicorn"}],
	}] with input as {"parsed": {"executable": "uv", "subcommand": "add", "arguments": ["uvicorn[standard]"], "flags": [], "options": {}}}
}

test_uv_add_pass1_incomplete_from_dev_option_value if {
	decisions[{
		"action": "incomplete",
		"require": [{"kind": "pypi_metadata", "package": "pytest-cov"}],
	}] with input as {"parsed": {"executable": "uv", "subcommand": "add", "arguments": [], "flags": [], "options": {"--dev": "pytest-cov"}}}
}

test_uv_add_pass2_allow_old_package if {
	decisions[{"action": "allow"}] with input as {
		"parsed": {"executable": "uv", "subcommand": "add", "arguments": ["fastapi"], "flags": [], "options": {}},
		"pypi_lookup_attempted": {"fastapi": true},
		"pypi_metadata": {"fastapi": {"age_days": 2000, "name": "fastapi", "first_version": "0.1.0"}},
	}
}

test_uv_add_pass2_deny_young_package_uses_stripped_key if {
	decisions[{
		"action": "deny",
		"reason": "Package 'uvicorn' is only 5 days old (first released 1.0.0). Policy requires packages to be at least 365 days old for security and stability.",
	}] with input as {
		"parsed": {"executable": "uv", "subcommand": "add", "arguments": ["uvicorn[standard]"], "flags": [], "options": {}},
		"pypi_lookup_attempted": {"uvicorn": true},
		"pypi_metadata": {"uvicorn": {"age_days": 5, "name": "uvicorn", "first_version": "1.0.0"}},
	}
}

test_uv_add_pass2_deny_not_found_after_lookup if {
	decisions[{
		"action": "deny",
		"reason": "Package not found on PyPI. Cannot verify package age for security policy.",
	}] with input as {
		"parsed": {"executable": "uv", "subcommand": "add", "arguments": ["totallyfake123"], "flags": [], "options": {}},
		"pypi_lookup_attempted": {"totallyfake123": true},
	}
}

test_uv_add_unsafe_flags_denied_without_pypi_lookup if {
	decisions[{
		"action": "deny",
		"reason": "uv add: unsupported flags detected. Only --dev, -d, --optional, and --group flags are allowed.",
	}] with input as {"parsed": {"executable": "uv", "subcommand": "add", "arguments": ["fastapi"], "flags": ["--unsafe-flag"], "options": {}}}
}
