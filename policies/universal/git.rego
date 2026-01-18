package universal

import data.helpers

# Git command policies
# - Allow common read operations (status, diff, log, show)
# - Allow safe write operations (add, commit, push, fetch, pull, checkout, mv)
# - Deny dangerous operations (push --force, rm, branch -D)

# Helper to check if git has a specific flag
has_git_flag(flag) if {
	input.parsed.flags[_] == flag
}

# Helper to check if git has force flag (--force or -f)
# Note: --force can be parsed as either a flag or an option depending on what follows
has_force_flag if {
	has_git_flag("--force")
}

has_force_flag if {
	has_git_flag("-f")
}

has_force_flag if {
	input.parsed.options["--force"]
}

has_force_flag if {
	input.parsed.options["-f"]
}

# Helper to check if git has specific option
has_git_option(opt) if {
	input.parsed.options[opt]
}

# git status - allow
decisions[decision] if {
	input.parsed.executable == "git"
	input.parsed.subcommand == "status"
	decision := {"action": "allow"}
}

# git diff - allow
decisions[decision] if {
	input.parsed.executable == "git"
	input.parsed.subcommand == "diff"
	decision := {"action": "allow"}
}

# git log - allow
decisions[decision] if {
	input.parsed.executable == "git"
	input.parsed.subcommand == "log"
	decision := {"action": "allow"}
}

# git show - allow
decisions[decision] if {
	input.parsed.executable == "git"
	input.parsed.subcommand == "show"
	decision := {"action": "allow"}
}

# git add -A - allow
decisions[decision] if {
	input.parsed.executable == "git"
	input.parsed.subcommand == "add"
	has_git_flag("-A")
	decision := {"action": "allow"}
}

# git add <safe paths> - allow
decisions[decision] if {
	input.parsed.executable == "git"
	input.parsed.subcommand == "add"
	not has_git_flag("-A")
	count(input.parsed.arguments) > 0
	every arg in input.parsed.arguments {
		helpers.is_safe_path(arg)
	}
	decision := {"action": "allow"}
}

# git commit with message or amend - allow
decisions[decision] if {
	input.parsed.executable == "git"
	input.parsed.subcommand == "commit"
	# Require one of: -m, --message, or --amend
	has_message_or_amend
	decision := {"action": "allow"}
}

# Helper to check if commit has message or amend
has_message_or_amend if {
	has_git_option("-m")
}

has_message_or_amend if {
	has_git_option("--message")
}

has_message_or_amend if {
	has_git_flag("--amend")
}

# git commit without message - deny
decisions[decision] if {
	input.parsed.executable == "git"
	input.parsed.subcommand == "commit"
	not has_message_or_amend
	decision := {
		"action": "deny",
		"reason": "`git commit` requires a message.\nUse `git commit -m \"message\"` or `git commit --amend`.",
	}
}

# git mv <safe paths> - allow
decisions[decision] if {
	input.parsed.executable == "git"
	input.parsed.subcommand == "mv"
	count(input.parsed.arguments) > 0
	every arg in input.parsed.arguments {
		helpers.is_safe_path(arg)
	}
	decision := {"action": "allow"}
}

# git mv with unsafe paths - deny
decisions[decision] if {
	input.parsed.executable == "git"
	input.parsed.subcommand == "mv"
	count(input.parsed.arguments) > 0
	some arg in input.parsed.arguments
	not helpers.is_safe_path(arg)
	decision := {
		"action": "deny",
		"reason": "git mv: only workspace-relative paths are allowed (no absolute paths, no ../, no /tmp)",
	}
}

# git checkout - allow
decisions[decision] if {
	input.parsed.executable == "git"
	input.parsed.subcommand == "checkout"
	decision := {"action": "allow"}
}

# git fetch - allow
decisions[decision] if {
	input.parsed.executable == "git"
	input.parsed.subcommand == "fetch"
	decision := {"action": "allow"}
}

# git pull - allow
decisions[decision] if {
	input.parsed.executable == "git"
	input.parsed.subcommand == "pull"
	decision := {"action": "allow"}
}

# git push without force - allow
decisions[decision] if {
	input.parsed.executable == "git"
	input.parsed.subcommand == "push"
	not has_force_flag
	decision := {"action": "allow"}
}

# git push --force or -f - deny
decisions[decision] if {
	input.parsed.executable == "git"
	input.parsed.subcommand == "push"
	has_force_flag
	decision := {
		"action": "deny",
		"reason": "Force push is not allowed.\nForce pushing can overwrite history and cause data loss for other collaborators.",
	}
}

# git rm - deny (use trash instead)
decisions[decision] if {
	input.parsed.executable == "git"
	input.parsed.subcommand == "rm"
	decision := {
		"action": "deny",
		"reason": "`git rm` is not allowed. Use `trash` instead.\nThe macOS `trash` command safely moves files to Trash.",
	}
}

# git branch -D - deny (force delete)
# Note: -D is parsed as an option with the branch name as value
decisions[decision] if {
	input.parsed.executable == "git"
	input.parsed.subcommand == "branch"
	input.parsed.options["-D"]
	decision := {
		"action": "deny",
		"reason": "`git branch -D` is not allowed.\nForce-deleting branches can result in data loss.",
	}
}
