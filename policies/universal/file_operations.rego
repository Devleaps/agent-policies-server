package universal

import data.helpers

# File operation commands with safe path validation
# Commands: cat, chmod, cp, cut, diff, du, ls, mkdir, sed, sort, tail, head

# Helper to check if all arguments are safe paths
all_args_safe(args) if {
	count(args) == 0
}

all_args_safe(args) if {
	count(args) > 0
	every arg in args {
		helpers.is_safe_path(arg)
	}
}

# Helper to check if all arguments and option values are safe paths
# This handles commands like "wc -l file.txt" where file.txt is in options
all_args_and_options_safe if {
	# Check arguments
	count(input.parsed.arguments) > 0
	every arg in input.parsed.arguments {
		helpers.is_safe_path(arg)
	}
}

all_args_and_options_safe if {
	# Check option values
	count(input.parsed.options) > 0
	every key, value in input.parsed.options {
		helpers.is_safe_path(value)
	}
}

all_args_and_options_safe if {
	# Allow if both are empty (command with no file arguments)
	count(input.parsed.arguments) == 0
	count(input.parsed.options) == 0
}

# Helper for [ command - filters out closing ] bracket from arguments
bracket_args_and_options_safe if {
	# Filter out ']' from arguments
	filtered_args := [arg | some arg in input.parsed.arguments; arg != "]"]

	# Check filtered arguments
	count(filtered_args) > 0
	every arg in filtered_args {
		helpers.is_safe_path(arg)
	}
}

bracket_args_and_options_safe if {
	# Check option values (same as all_args_and_options_safe)
	count(input.parsed.options) > 0
	every key, value in input.parsed.options {
		helpers.is_safe_path(value)
	}
}

bracket_args_and_options_safe if {
	# Filter out ']' from arguments
	filtered_args := [arg | some arg in input.parsed.arguments; arg != "]"]

	# Allow if both filtered args and options are empty
	count(filtered_args) == 0
	count(input.parsed.options) == 0
}

# Allow cat with safe paths
decisions[decision] if {
	input.parsed.executable == "cat"
	all_args_safe(input.parsed.arguments)
	decision := {"action": "allow"}
}

# Deny cat with unsafe paths
decisions[decision] if {
	input.parsed.executable == "cat"
	not all_args_safe(input.parsed.arguments)
	decision := {
		"action": "deny",
		"reason": "cat: only workspace-relative paths are allowed (no absolute paths, no ../, no /tmp)",
	}
}

# Allow chmod with safe paths
decisions[decision] if {
	input.parsed.executable == "chmod"
	all_args_safe(input.parsed.arguments)
	decision := {"action": "allow"}
}

# Deny chmod with unsafe paths
decisions[decision] if {
	input.parsed.executable == "chmod"
	not all_args_safe(input.parsed.arguments)
	decision := {
		"action": "deny",
		"reason": "chmod: only workspace-relative paths are allowed (no absolute paths, no ../, no /tmp). Modifying permissions on system files or sensitive directories is not allowed.",
	}
}

# Allow cp with safe paths
decisions[decision] if {
	input.parsed.executable == "cp"
	all_args_safe(input.parsed.arguments)
	decision := {"action": "allow"}
}

# Deny cp with unsafe paths
decisions[decision] if {
	input.parsed.executable == "cp"
	not all_args_safe(input.parsed.arguments)
	decision := {
		"action": "deny",
		"reason": "cp: only workspace-relative paths are allowed (no absolute paths, no ../, no /tmp)",
	}
}

# Allow cut with safe paths
decisions[decision] if {
	input.parsed.executable == "cut"
	all_args_safe(input.parsed.arguments)
	decision := {"action": "allow"}
}

# Deny cut with unsafe paths
decisions[decision] if {
	input.parsed.executable == "cut"
	not all_args_safe(input.parsed.arguments)
	decision := {
		"action": "deny",
		"reason": "cut: only workspace-relative paths are allowed (no absolute paths, no ../, no /tmp)",
	}
}

# Allow diff with safe paths
decisions[decision] if {
	input.parsed.executable == "diff"
	all_args_safe(input.parsed.arguments)
	decision := {"action": "allow"}
}

# Deny diff with unsafe paths
decisions[decision] if {
	input.parsed.executable == "diff"
	not all_args_safe(input.parsed.arguments)
	decision := {
		"action": "deny",
		"reason": "diff: only workspace-relative paths are allowed (no absolute paths, no ../, no /tmp)",
	}
}

# Allow du with safe paths
decisions[decision] if {
	input.parsed.executable == "du"
	all_args_safe(input.parsed.arguments)
	decision := {"action": "allow"}
}

# Deny du with unsafe paths
decisions[decision] if {
	input.parsed.executable == "du"
	not all_args_safe(input.parsed.arguments)
	decision := {
		"action": "deny",
		"reason": "du: only workspace-relative paths are allowed (no absolute paths, no ../, no /tmp)",
	}
}

# Allow ls with safe paths
decisions[decision] if {
	input.parsed.executable == "ls"
	all_args_safe(input.parsed.arguments)
	decision := {"action": "allow"}
}

# Deny ls with unsafe paths
decisions[decision] if {
	input.parsed.executable == "ls"
	not all_args_safe(input.parsed.arguments)
	decision := {
		"action": "deny",
		"reason": "ls: only workspace-relative paths are allowed (no absolute paths, no ../, no /tmp)",
	}
}

# Allow mkdir with safe paths
decisions[decision] if {
	input.parsed.executable == "mkdir"
	all_args_safe(input.parsed.arguments)
	decision := {"action": "allow"}
}

# Deny mkdir with unsafe paths
decisions[decision] if {
	input.parsed.executable == "mkdir"
	not all_args_safe(input.parsed.arguments)
	decision := {
		"action": "deny",
		"reason": "mkdir: only workspace-relative paths are allowed (no absolute paths, no ../, no /tmp)",
	}
}

# Allow sed with safe paths
decisions[decision] if {
	input.parsed.executable == "sed"
	all_args_safe(input.parsed.arguments)
	decision := {"action": "allow"}
}

# Deny sed with unsafe paths
decisions[decision] if {
	input.parsed.executable == "sed"
	not all_args_safe(input.parsed.arguments)
	decision := {
		"action": "deny",
		"reason": "sed: only workspace-relative paths are allowed (no absolute paths, no ../, no /tmp)",
	}
}

# Allow sort with safe paths
decisions[decision] if {
	input.parsed.executable == "sort"
	all_args_safe(input.parsed.arguments)
	decision := {"action": "allow"}
}

# Deny sort with unsafe paths
decisions[decision] if {
	input.parsed.executable == "sort"
	not all_args_safe(input.parsed.arguments)
	decision := {
		"action": "deny",
		"reason": "sort: only workspace-relative paths are allowed (no absolute paths, no ../, no /tmp)",
	}
}

# Allow tail with safe paths
decisions[decision] if {
	input.parsed.executable == "tail"
	all_args_safe(input.parsed.arguments)
	decision := {"action": "allow"}
}

# Deny tail with unsafe paths
decisions[decision] if {
	input.parsed.executable == "tail"
	not all_args_safe(input.parsed.arguments)
	decision := {
		"action": "deny",
		"reason": "tail: only workspace-relative paths are allowed (no absolute paths, no ../, no /tmp)",
	}
}

# Allow head with safe paths
decisions[decision] if {
	input.parsed.executable == "head"
	all_args_safe(input.parsed.arguments)
	decision := {"action": "allow"}
}

# Deny head with unsafe paths
decisions[decision] if {
	input.parsed.executable == "head"
	not all_args_safe(input.parsed.arguments)
	decision := {
		"action": "deny",
		"reason": "head: only workspace-relative paths are allowed (no absolute paths, no ../, no /tmp)",
	}
}

# Always allow commands (no path arguments required)
decisions[decision] if {
	input.parsed.executable == "grep"
	decision := {"action": "allow"}
}

decisions[decision] if {
	input.parsed.executable == "lsof"
	decision := {"action": "allow"}
}

decisions[decision] if {
	input.parsed.executable == "pkill"
	decision := {"action": "allow"}
}

decisions[decision] if {
	input.parsed.executable == "ps"
	decision := {"action": "allow"}
}

decisions[decision] if {
	input.parsed.executable == "pwd"
	decision := {"action": "allow"}
}

decisions[decision] if {
	input.parsed.executable == "echo"
	decision := {"action": "allow"}
}

decisions[decision] if {
	input.parsed.executable == "nslookup"
	decision := {"action": "allow"}
}

decisions[decision] if {
	input.parsed.executable == "pytest"
	decision := {"action": "allow"}
}

decisions[decision] if {
	input.parsed.executable == "tflint"
	decision := {"action": "allow"}
}

# opa test - allow policy testing
decisions[decision] if {
	input.parsed.executable == "opa"
	count(input.parsed.arguments) > 0
	input.parsed.arguments[0] == "test"
	decision := {"action": "allow"}
}

decisions[decision] if {
	input.parsed.executable == "which"
	decision := {"action": "allow"}
}

decisions[decision] if {
	input.parsed.executable == "true"
	decision := {"action": "allow"}
}

# mv - move/rename files (safe paths required)
decisions[decision] if {
	input.parsed.executable == "mv"
	all_args_safe(input.parsed.arguments)
	decision := {"action": "allow"}
}

decisions[decision] if {
	input.parsed.executable == "mv"
	not all_args_safe(input.parsed.arguments)
	decision := {
		"action": "deny",
		"reason": "mv: only workspace-relative paths are allowed (no absolute paths, no ../, no /tmp)",
	}
}

# rmdir - remove empty directories (safe paths required)
decisions[decision] if {
	input.parsed.executable == "rmdir"
	all_args_safe(input.parsed.arguments)
	decision := {"action": "allow"}
}

decisions[decision] if {
	input.parsed.executable == "rmdir"
	not all_args_safe(input.parsed.arguments)
	decision := {
		"action": "deny",
		"reason": "rmdir: only workspace-relative paths are allowed (no absolute paths, no ../, no /tmp)",
	}
}

# touch - create/update files (safe paths required)
decisions[decision] if {
	input.parsed.executable == "touch"
	all_args_safe(input.parsed.arguments)
	decision := {"action": "allow"}
}

decisions[decision] if {
	input.parsed.executable == "touch"
	not all_args_safe(input.parsed.arguments)
	decision := {
		"action": "deny",
		"reason": "touch: only workspace-relative paths are allowed (no absolute paths, no ../, no /tmp)",
	}
}

# trash - macOS trash command (safe paths required)
decisions[decision] if {
	input.parsed.executable == "trash"
	all_args_and_options_safe
	decision := {"action": "allow"}
}

decisions[decision] if {
	input.parsed.executable == "trash"
	not all_args_and_options_safe
	decision := {
		"action": "deny",
		"reason": "trash: only workspace-relative paths are allowed (no absolute paths, no ../, no /tmp)",
	}
}

# wc - word count (safe paths required)
decisions[decision] if {
	input.parsed.executable == "wc"
	all_args_and_options_safe
	decision := {"action": "allow"}
}

decisions[decision] if {
	input.parsed.executable == "wc"
	not all_args_and_options_safe
	decision := {
		"action": "deny",
		"reason": "wc: only workspace-relative paths are allowed (no absolute paths, no ../, no /tmp)",
	}
}

# test - shell built-in for file/string tests (safe paths required)
decisions[decision] if {
	input.parsed.executable == "test"
	all_args_and_options_safe
	decision := {"action": "allow"}
}

decisions[decision] if {
	input.parsed.executable == "test"
	not all_args_and_options_safe
	decision := {
		"action": "deny",
		"reason": "test: only workspace-relative paths are allowed (no absolute paths, no ../, no /tmp)",
	}
}

# [ - alias for test command (safe paths required)
decisions[decision] if {
	input.parsed.executable == "["
	bracket_args_and_options_safe
	decision := {"action": "allow"}
}

decisions[decision] if {
	input.parsed.executable == "["
	not bracket_args_and_options_safe
	decision := {
		"action": "deny",
		"reason": "[: only workspace-relative paths are allowed (no absolute paths, no ../, no /tmp)",
	}
}

# tree - visualize directory structure (safe paths required)
decisions[decision] if {
	input.parsed.executable == "tree"
	all_args_safe(input.parsed.arguments)
	decision := {"action": "allow"}
}

decisions[decision] if {
	input.parsed.executable == "tree"
	not all_args_safe(input.parsed.arguments)
	decision := {
		"action": "deny",
		"reason": "tree: Only workspace-relative paths are allowed (no absolute paths, no ../, no /tmp).",
	}
}

# rm - always denied, use trash instead
decisions[decision] if {
	input.parsed.executable == "rm"
	decision := {
		"action": "deny",
		"reason": "The rm command is not allowed. Always use trash instead. The macOS trash command safely moves files to Trash.",
	}
}
