package universal

# sqlite3 command policies
# - Only allow SELECT queries (read-only)
# - Deny write operations (INSERT, UPDATE, DELETE, DROP, etc.)

# Convert command to uppercase for case-insensitive matching
command_upper := upper(input.event.command)

# Check for write operations using word boundaries
has_write_operation if {
	write_ops := ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "REPLACE", "ATTACH", "DETACH", "TRUNCATE", "BEGIN", "COMMIT", "ROLLBACK", "VACUUM", "REINDEX", "ANALYZE"]
	some op in write_ops

	# Use regex with word boundaries - pattern must match entire string in Rego
	# So we use .* before and after to match the whole command
	pattern := sprintf(".*\\b%s\\b.*", [op])
	regex.match(pattern, command_upper)
}

# Check for SELECT operation
has_select if {
	contains(command_upper, "SELECT")
}

# Check for read-only PRAGMA
has_readonly_pragma if {
	contains(command_upper, "PRAGMA")
}

# Check for EXPLAIN query
has_explain if {
	contains(command_upper, "EXPLAIN")
}

# Check for dot commands (.schema, .tables)
has_dot_command if {
	contains(command_upper, ".SCHEMA")
}

has_dot_command if {
	contains(command_upper, ".TABLES")
}

# Deny write operations
decisions[decision] if {
	input.parsed.executable == "sqlite3"
	has_write_operation
	decision := {
		"action": "deny",
		"reason": "By policy, sqlite3 write operations (INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, REPLACE, ATTACH, DETACH, TRUNCATE, BEGIN, COMMIT, ROLLBACK, VACUUM, REINDEX, ANALYZE) are not allowed. Only SELECT queries are permitted for database read operations.",
	}
}

# Allow SELECT queries
decisions[decision] if {
	input.parsed.executable == "sqlite3"
	not has_write_operation
	has_select
	decision := {"action": "allow"}
}

# Allow read-only PRAGMA
decisions[decision] if {
	input.parsed.executable == "sqlite3"
	not has_write_operation
	has_readonly_pragma
	decision := {"action": "allow"}
}

# Allow EXPLAIN queries
decisions[decision] if {
	input.parsed.executable == "sqlite3"
	not has_write_operation
	has_explain
	decision := {"action": "allow"}
}

# Allow dot commands
decisions[decision] if {
	input.parsed.executable == "sqlite3"
	not has_write_operation
	has_dot_command
	decision := {"action": "allow"}
}
