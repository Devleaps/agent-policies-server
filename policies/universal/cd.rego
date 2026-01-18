package universal

import data.helpers

# cd command policies
# - Allow upward navigation (only .. segments like "..", "../..", "../../..")
# - Allow safe relative paths
# - Deny unsafe paths

# Helper: check if path is upward navigation (only .. segments)
is_upward_navigation(path) if {
	segments := split(path, "/")
	count(segments) > 0
	every segment in segments {
		segment == ".."
	}
}

# Allow cd with upward navigation (e.g., "..", "../..", "../../..")
decisions[decision] if {
	input.parsed.executable == "cd"
	count(input.parsed.arguments) > 0
	path := input.parsed.arguments[0]
	is_upward_navigation(path)
	decision := {"action": "allow"}
}

# Allow cd with safe relative paths
decisions[decision] if {
	input.parsed.executable == "cd"
	count(input.parsed.arguments) > 0
	path := input.parsed.arguments[0]
	not is_upward_navigation(path)
	helpers.is_safe_path(path)
	decision := {"action": "allow"}
}

# Deny cd with unsafe paths
decisions[decision] if {
	input.parsed.executable == "cd"
	count(input.parsed.arguments) > 0
	path := input.parsed.arguments[0]
	not is_upward_navigation(path)
	not helpers.is_safe_path(path)
	decision := {
		"action": "deny",
		"reason": "By policy, cd with unsafe path.\nUse relative paths only (e.g., `cd subdir` or `cd project/src`).\nIf you need to navigate upward, use paths like `cd ..` or `cd ../..`.",
	}
}
