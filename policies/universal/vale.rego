package universal

import rego.v1

# Vale - A markup-aware linter for prose
# https://vale.sh/docs/cli
#
# All Vale commands are safe (read-only or project setup):
# - vale <files>    : Lint prose files (read-only)
# - vale sync       : Download style packages to local StylesPath
# - vale ls-*       : Print configuration/directories/metrics/vars
# - All flags are safe
#
# Vale never modifies source files - it's a pure linter

# Allow all vale commands with workspace-relative paths
decisions[decision] if {
	input.parsed.executable == "vale"

	# Check all arguments are workspace-relative (if any)
	every arg in input.parsed.arguments {
		helpers.is_safe_path(arg)
	}

	decision := {"action": "allow"}
}

# Deny vale with absolute paths or path traversal
decisions[decision] if {
	input.parsed.executable == "vale"
	count(input.parsed.arguments) > 0
	some arg in input.parsed.arguments
	not helpers.is_safe_path(arg)

	decision := {
		"action": "deny",
		"reason": sprintf("vale paths must be workspace-relative (no absolute paths, no ../): %s", [arg]),
	}
}
