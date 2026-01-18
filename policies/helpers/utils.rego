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

# Localhost URL validation
# Accepts: localhost, 127.x.x.x, ::1
# Split by '?' first to avoid matching localhost in query params
is_localhost_url(url) if {
	parts := split(url, "?")
	contains(parts[0], "://localhost")
}

is_localhost_url(url) if {
	parts := split(url, "?")
	contains(parts[0], "://127.")
}

is_localhost_url(url) if {
	parts := split(url, "?")
	contains(parts[0], "://[::1]")
}
