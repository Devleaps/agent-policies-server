package universal

import data.helpers

# Redirect path validation
# Special case: /dev/null is allowed
# Everything else must be workspace-relative

# Helper to check if redirect is to /dev/null
is_dev_null("/dev/null")

# Deny commands with unsafe redirects
decisions contains decision if {
	decision := {
		"action": "deny",
		"reason": concat("", [
			"Redirects must use workspace-relative paths (no absolute paths, no ../, no /tmp). ",
			"Exception: /dev/null is allowed.",
		]),
	}

	some redirect in input.parsed.redirects
	path := redirect.path

	# Allow /dev/null
	not is_dev_null(path)

	# Everything else must be workspace-relative
	not helpers.is_safe_path(path)
}
