package universal

import data.helpers

# Cloud CLI tool policies
# - docker: Allow build with safe paths
# - gh: Allow api with GET only
# - terraform: Allow fmt and plan only
# - terragrunt: Allow plan only
# - az: Allow list and show only
# - kubectl/k: Allow read-only operations

# docker build with safe paths - allow
decisions[decision] if {
	input.parsed.executable == "docker"
	input.parsed.subcommand == "build"
	count(input.parsed.arguments) > 0
	every arg in input.parsed.arguments {
		helpers.is_safe_path(arg)
	}
	decision := {"action": "allow"}
}

# docker build with no arguments - allow
decisions[decision] if {
	input.parsed.executable == "docker"
	input.parsed.subcommand == "build"
	count(input.parsed.arguments) == 0
	decision := {"action": "allow"}
}

# docker build with unsafe paths - deny
decisions[decision] if {
	input.parsed.executable == "docker"
	input.parsed.subcommand == "build"
	count(input.parsed.arguments) > 0
	some arg in input.parsed.arguments
	not helpers.is_safe_path(arg)
	decision := {
		"action": "deny",
		"reason": "docker build: only workspace-relative paths are allowed (no absolute paths, no ../, no /tmp)",
	}
}

# gh read-only subcommands (resources that support list/view/status)
gh_read_only_resources := ["issue", "pr", "repo", "run", "workflow", "release", "gist", "project", "label", "milestone"]

# gh read-only actions
gh_read_only_actions := ["list", "view", "status"]

# gh resource list/view/status - allow
decisions[decision] if {
	input.parsed.executable == "gh"
	some resource in gh_read_only_resources
	input.parsed.subcommand == resource
	count(input.parsed.arguments) > 0
	some action in gh_read_only_actions
	input.parsed.arguments[0] == action
	decision := {"action": "allow"}
}

# gh auth status - allow
decisions[decision] if {
	input.parsed.executable == "gh"
	input.parsed.subcommand == "auth"
	count(input.parsed.arguments) > 0
	input.parsed.arguments[0] == "status"
	decision := {"action": "allow"}
}

# gh api with GET - allow
decisions[decision] if {
	input.parsed.executable == "gh"
	input.parsed.subcommand == "api"
	input.parsed.options["--method"] == "GET"
	decision := {"action": "allow"}
}

# gh api without explicit GET method - deny
decisions[decision] if {
	input.parsed.executable == "gh"
	input.parsed.subcommand == "api"
	not input.parsed.options["--method"]
	decision := {
		"action": "deny",
		"reason": "gh api requires explicit --method GET.\nOnly GET requests are allowed for safety.",
	}
}

# gh api with non-GET method - deny
decisions[decision] if {
	input.parsed.executable == "gh"
	input.parsed.subcommand == "api"
	input.parsed.options["--method"]
	input.parsed.options["--method"] != "GET"
	decision := {
		"action": "deny",
		"reason": "Only GET method is allowed for gh api.\nPOST, PUT, DELETE, and PATCH are not permitted.",
	}
}

# terraform fmt - allow
decisions[decision] if {
	input.parsed.executable == "terraform"
	input.parsed.subcommand == "fmt"
	decision := {"action": "allow"}
}

# terraform plan - allow
decisions[decision] if {
	input.parsed.executable == "terraform"
	input.parsed.subcommand == "plan"
	decision := {"action": "allow"}
}

# terraform other commands - deny
decisions[decision] if {
	input.parsed.executable == "terraform"
	input.parsed.subcommand != "fmt"
	input.parsed.subcommand != "plan"
	decision := {
		"action": "deny",
		"reason": "Only `terraform fmt` and `terraform plan` are allowed.\nDangerous operations like apply, destroy, or init are not permitted.",
	}
}

# terragrunt plan - allow
decisions[decision] if {
	input.parsed.executable == "terragrunt"
	input.parsed.subcommand == "plan"
	decision := {"action": "allow"}
}

# terragrunt other commands - deny
decisions[decision] if {
	input.parsed.executable == "terragrunt"
	input.parsed.subcommand != "plan"
	decision := {
		"action": "deny",
		"reason": "Only `terragrunt plan` is allowed.\nDangerous operations like apply, destroy, or run-all are not permitted.",
	}
}

# Helper: check if az subcommand or last arg is "list"
az_has_list if {
	input.parsed.subcommand == "list"
}

az_has_list if {
	count(input.parsed.arguments) > 0
	input.parsed.arguments[count(input.parsed.arguments) - 1] == "list"
}

# Helper: check if az subcommand or last arg is "show"
az_has_show if {
	input.parsed.subcommand == "show"
}

az_has_show if {
	count(input.parsed.arguments) > 0
	input.parsed.arguments[count(input.parsed.arguments) - 1] == "show"
}

# az list - allow
decisions[decision] if {
	input.parsed.executable == "az"
	az_has_list
	decision := {"action": "allow"}
}

# az show - allow
decisions[decision] if {
	input.parsed.executable == "az"
	not az_has_list
	az_has_show
	decision := {"action": "allow"}
}

# az other commands - deny
decisions[decision] if {
	input.parsed.executable == "az"
	not az_has_list
	not az_has_show
	decision := {
		"action": "deny",
		"reason": "Only Azure CLI read-only commands with 'list' or 'show' are allowed.\nDangerous operations like create, delete, update, or set are not permitted.",
	}
}

# kubectl/k read-only subcommands
kubectl_read_only_subcommands := ["get", "list", "describe", "logs", "top", "version", "api-versions", "api-resources", "explain", "cluster-info"]

# kubectl read-only subcommands - allow
decisions[decision] if {
	input.parsed.executable == "kubectl"
	some subcommand in kubectl_read_only_subcommands
	input.parsed.subcommand == subcommand
	decision := {"action": "allow"}
}

# kubectl config view - allow
decisions[decision] if {
	input.parsed.executable == "kubectl"
	input.parsed.subcommand == "config"
	count(input.parsed.arguments) > 0
	input.parsed.arguments[0] == "view"
	decision := {"action": "allow"}
}

# kubectl auth can-i - allow
decisions[decision] if {
	input.parsed.executable == "kubectl"
	input.parsed.subcommand == "auth"
	count(input.parsed.arguments) > 0
	input.parsed.arguments[0] == "can-i"
	decision := {"action": "allow"}
}

# kubectl other commands - deny
decisions[decision] if {
	input.parsed.executable == "kubectl"
	not kubectl_is_allowed
	decision := {
		"action": "deny",
		"reason": "Only read-only kubectl operations are allowed",
	}
}

# Helper to check if kubectl command is allowed
kubectl_is_allowed if {
	some subcommand in kubectl_read_only_subcommands
	input.parsed.subcommand == subcommand
}

kubectl_is_allowed if {
	input.parsed.subcommand == "config"
	count(input.parsed.arguments) > 0
	input.parsed.arguments[0] == "view"
}

kubectl_is_allowed if {
	input.parsed.subcommand == "auth"
	count(input.parsed.arguments) > 0
	input.parsed.arguments[0] == "can-i"
}

# k (kubectl alias) read-only subcommands - allow
decisions[decision] if {
	input.parsed.executable == "k"
	some subcommand in kubectl_read_only_subcommands
	input.parsed.subcommand == subcommand
	decision := {"action": "allow"}
}

# k config view - allow
decisions[decision] if {
	input.parsed.executable == "k"
	input.parsed.subcommand == "config"
	count(input.parsed.arguments) > 0
	input.parsed.arguments[0] == "view"
	decision := {"action": "allow"}
}

# k auth can-i - allow
decisions[decision] if {
	input.parsed.executable == "k"
	input.parsed.subcommand == "auth"
	count(input.parsed.arguments) > 0
	input.parsed.arguments[0] == "can-i"
	decision := {"action": "allow"}
}

# k other commands - deny
decisions[decision] if {
	input.parsed.executable == "k"
	not k_is_allowed
	decision := {
		"action": "deny",
		"reason": "Only read-only kubectl operations are allowed",
	}
}

# Helper to check if k command is allowed
k_is_allowed if {
	some subcommand in kubectl_read_only_subcommands
	input.parsed.subcommand == subcommand
}

k_is_allowed if {
	input.parsed.subcommand == "config"
	count(input.parsed.arguments) > 0
	input.parsed.arguments[0] == "view"
}

k_is_allowed if {
	input.parsed.subcommand == "auth"
	count(input.parsed.arguments) > 0
	input.parsed.arguments[0] == "can-i"
}
