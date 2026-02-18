package universal

import data.helpers

# GitHub CLI command policies
# - Allow read-only operations (pr view/diff/list, issue view/list, repo view)
# - Deny write operations (pr create/merge/close, issue create/close)

# Read-only gh pr subcommands
gh_pr_read_subcommands := ["view", "diff", "list", "checks", "status"]

# Read-only gh issue subcommands
gh_issue_read_subcommands := ["view", "list", "status"]

# Read-only gh repo subcommands
gh_repo_read_subcommands := ["view", "list"]

# Read-only gh run subcommands (GitHub Actions)
gh_run_read_subcommands := ["view", "list", "watch"]

# Read-only gh workflow subcommands
gh_workflow_read_subcommands := ["view", "list"]

# gh pr - read-only operations
decisions[decision] if {
	input.parsed.executable == "gh"
	input.parsed.subcommand == "pr"
	count(input.parsed.arguments) > 0
	input.parsed.arguments[0] in gh_pr_read_subcommands
	decision := {"action": "allow"}
}

# gh issue - read-only operations
decisions[decision] if {
	input.parsed.executable == "gh"
	input.parsed.subcommand == "issue"
	count(input.parsed.arguments) > 0
	input.parsed.arguments[0] in gh_issue_read_subcommands
	decision := {"action": "allow"}
}

# gh repo - read-only operations
decisions[decision] if {
	input.parsed.executable == "gh"
	input.parsed.subcommand == "repo"
	count(input.parsed.arguments) > 0
	input.parsed.arguments[0] in gh_repo_read_subcommands
	decision := {"action": "allow"}
}

# gh run - read-only operations
decisions[decision] if {
	input.parsed.executable == "gh"
	input.parsed.subcommand == "run"
	count(input.parsed.arguments) > 0
	input.parsed.arguments[0] in gh_run_read_subcommands
	decision := {"action": "allow"}
}

# gh workflow - read-only operations
decisions[decision] if {
	input.parsed.executable == "gh"
	input.parsed.subcommand == "workflow"
	count(input.parsed.arguments) > 0
	input.parsed.arguments[0] in gh_workflow_read_subcommands
	decision := {"action": "allow"}
}

# gh auth status - read-only
decisions[decision] if {
	input.parsed.executable == "gh"
	input.parsed.subcommand == "auth"
	count(input.parsed.arguments) > 0
	input.parsed.arguments[0] == "status"
	decision := {"action": "allow"}
}

# gh api - allow GET requests only
decisions[decision] if {
	input.parsed.executable == "gh"
	input.parsed.subcommand == "api"
	# Default method is GET, so allow if no method specified or method is GET
	not input.parsed.options["-X"]
	not input.parsed.options["--method"]
	decision := {"action": "allow"}
}

decisions[decision] if {
	input.parsed.executable == "gh"
	input.parsed.subcommand == "api"
	input.parsed.options["-X"] == "GET"
	decision := {"action": "allow"}
}

decisions[decision] if {
	input.parsed.executable == "gh"
	input.parsed.subcommand == "api"
	input.parsed.options["--method"] == "GET"
	decision := {"action": "allow"}
}

# gh api - deny non-GET requests
decisions[decision] if {
	input.parsed.executable == "gh"
	input.parsed.subcommand == "api"
	input.parsed.options["-X"]
	input.parsed.options["-X"] != "GET"
	decision := {
		"action": "deny",
		"reason": "gh api: only GET requests are allowed (use --method GET or omit for read-only access)",
	}
}

decisions[decision] if {
	input.parsed.executable == "gh"
	input.parsed.subcommand == "api"
	input.parsed.options["--method"]
	input.parsed.options["--method"] != "GET"
	decision := {
		"action": "deny",
		"reason": "gh api: only GET requests are allowed (use --method GET or omit for read-only access)",
	}
}
