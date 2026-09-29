package universal

import data.helpers

# Regal - a linter for Rego
# https://docs.styra.com/regal
# - brew install regal : allow installing this one formula
# - regal lint <paths> : read-only, workspace-relative paths only
# Other regal commands (fix, new, update) modify files and defer to the user.

decisions[decision] if {
	input.parsed.executable == "brew"
	input.parsed.arguments == ["install", "regal"]
	count(input.parsed.flags) == 0
	count(input.parsed.options) == 0
	decision := {"action": "allow"}
}

regal_lint_paths_safe if {
	every arg in array.slice(input.parsed.arguments, 1, count(input.parsed.arguments)) {
		helpers.is_safe_path(arg)
	}
	every _, value in input.parsed.options {
		helpers.is_safe_path(value)
	}
}

decisions[decision] if {
	input.parsed.executable == "regal"
	count(input.parsed.arguments) > 0
	input.parsed.arguments[0] == "lint"
	regal_lint_paths_safe
	decision := {"action": "allow"}
}

decisions[decision] if {
	input.parsed.executable == "regal"
	count(input.parsed.arguments) > 0
	input.parsed.arguments[0] == "lint"
	not regal_lint_paths_safe
	decision := {
		"action": "deny",
		"reason": "regal lint: only workspace-relative paths are allowed (no absolute paths, no ../, no /tmp)",
	}
}
