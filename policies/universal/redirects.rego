package universal

# Redirect path validation

# Helper to check if redirect path is unsafe
is_unsafe_redirect(path) if {
	startswith(path, "/tmp/")
}

is_unsafe_redirect(path) if {
	startswith(path, "/home/")
}

is_unsafe_redirect(path) if {
	startswith(path, "/etc/")
}

# Deny commands with unsafe redirects
decisions[decision] if {
	count(input.parsed.redirects) > 0
	some redirect in input.parsed.redirects
	# redirect is a dict with "op" and "path" fields
	path := redirect.path
	is_unsafe_redirect(path)
	decision := {
		"action": "deny",
		"reason": "Writing to `/tmp/`, `/home/`, or `/etc/` is not allowed.\nUse workspace-relative paths instead.",
	}
}
