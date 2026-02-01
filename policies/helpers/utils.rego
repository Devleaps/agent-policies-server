package helpers

# Path validation
# Checks for unsafe paths: absolute paths, home directory, path traversal, /tmp
is_safe_path(path) if {
	not startswith(path, "/")
	not startswith(path, "~")
	not contains(path, "../")
	not contains(path, "/..")
	path != ".."
	not startswith(path, "/tmp")
}

# Localhost URL validation - defensive against subdomain attacks
# Accepts ONLY: localhost, 127.x.x.x, ::1 as the actual hostname
# Rejects: localhost.evil.com, 127.0.0.1.evil.com, evil.com/localhost, etc.

# Helper to check if URL matches localhost exactly (not subdomain)
is_localhost_url(url) if {
	# Remove query params first
	parts := split(url, "?")
	base_url := parts[0]

	# Check for ://localhost: (with port)
	contains(base_url, "://localhost:")
}

is_localhost_url(url) if {
	# Remove query params first
	parts := split(url, "?")
	base_url := parts[0]

	# Check for ://localhost/ (with path)
	contains(base_url, "://localhost/")
}

is_localhost_url(url) if {
	# Remove query params first
	parts := split(url, "?")
	base_url := parts[0]

	# Check for ://localhost at end (no port, no path)
	endswith(base_url, "://localhost")
}

# Helper to check if URL matches 127.x.x.x exactly (not subdomain)
is_localhost_url(url) if {
	# Remove query params first
	parts := split(url, "?")
	base_url := parts[0]

	# Check for ://127.: (with port) and ensure it ends with : or /
	contains(base_url, "://127.")

	# Extract part after ://
	scheme_parts := split(base_url, "://")
	count(scheme_parts) == 2
	host_part := scheme_parts[1]

	# Must start with 127.
	startswith(host_part, "127.")

	# Must be followed by port or path (not subdomain)
	# Split by / to get host:port part
	path_parts := split(host_part, "/")
	host_and_port := path_parts[0]

	# Split by : to check for subdomain attack
	# Valid: 127.0.0.1:8080 -> no dots after first segment
	# Invalid: 127.0.0.1.evil.com -> dots after
	colon_parts := split(host_and_port, ":")

	# If there's a colon, everything before it should be 127.x.x.x
	# If no colon, the whole thing should be 127.x.x.x
	# Count dots in the host part (before colon)
	ip_part := colon_parts[0]

	# Valid 127.x.x.x has exactly 3 dots, nothing more
	not contains(ip_part, "..") # no double dots
	count(split(ip_part, ".")) == 4 # exactly 4 octets
}

# Helper to check if URL matches [::1] exactly
is_localhost_url(url) if {
	# Remove query params first
	parts := split(url, "?")
	base_url := parts[0]

	# Check for ://[::1]: (with port)
	contains(base_url, "://[::1]:")
}

is_localhost_url(url) if {
	# Remove query params first
	parts := split(url, "?")
	base_url := parts[0]

	# Check for ://[::1]/ (with path)
	contains(base_url, "://[::1]/")
}

is_localhost_url(url) if {
	# Remove query params first
	parts := split(url, "?")
	base_url := parts[0]

	# Check for ://[::1] at end
	endswith(base_url, "://[::1]")
}
