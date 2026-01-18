package universal

import data.helpers

# find command policies
# - Deny find with -exec (security risk)
# - Require safe paths

# Check if -exec option exists
has_exec_option if {
	input.parsed.options["-exec"]
}

# Deny find with -exec option
decisions[decision] if {
	input.parsed.executable == "find"
	has_exec_option
	decision := {
		"action": "deny",
		"reason": "find commands with -exec are not allowed for security reasons",
	}
}

# Helper to check if all find arguments are safe paths
all_find_args_safe(args) if {
	count(args) > 0
	every arg in args {
		helpers.is_safe_path(arg)
	}
}

# Allow find with safe paths (and no -exec)
decisions[decision] if {
	input.parsed.executable == "find"
	not has_exec_option
	all_find_args_safe(input.parsed.arguments)
	decision := {"action": "allow"}
}

# Deny find with unsafe paths
decisions[decision] if {
	input.parsed.executable == "find"
	not has_exec_option
	not all_find_args_safe(input.parsed.arguments)
	decision := {
		"action": "deny",
		"reason": "By policy, find must use safe paths.\nUse relative paths only (e.g., `find . -name \"*.txt\"` or `find subdir -type f`).\nIf you need to search upward, first `cd` to the target directory.",
	}
}
