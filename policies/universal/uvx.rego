package universal

import data.helpers

# uvx command policies
# - Allow whitelisted tools (black, mypy, bandit, ruff)
# - Options that change which package runs (--from, --with, indexes) defer to
#   the user: "uvx --from other-pkg ruff" runs other-pkg, not ruff
# - --directory must be workspace-relative

# Whitelisted uvx tools
uvx_allowed_tools := ["black", "mypy", "bandit", "ruff"]

uvx_package_source_options := {
	"--from",
	"--with",
	"-w",
	"--with-editable",
	"--with-requirements",
	"--index",
	"--index-url",
	"-i",
	"--extra-index-url",
	"--default-index",
	"--find-links",
	"-f",
	"--config-file",
}

uvx_changes_package if {
	some key, _ in input.parsed.options
	key in uvx_package_source_options
}

uvx_changes_package if {
	some flag in input.parsed.flags
	flag in uvx_package_source_options
}

uvx_unsafe_directory if {
	directory := input.parsed.options["--directory"]
	not helpers.is_safe_path(directory)
}

# Allow whitelisted uvx tools
decisions[decision] if {
	input.parsed.executable == "uvx"
	count(input.parsed.arguments) > 0
	input.parsed.arguments[0] in uvx_allowed_tools
	not uvx_changes_package
	not uvx_unsafe_directory
	decision := {"action": "allow"}
}

# Deny uvx --directory outside the workspace
decisions[decision] if {
	input.parsed.executable == "uvx"
	uvx_unsafe_directory
	decision := {
		"action": "deny",
		"reason": "uvx --directory: only workspace-relative paths are allowed (no absolute paths, no ../, no /tmp)",
	}
}
