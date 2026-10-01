package universal

import data.helpers

# Cloud CLI tool policies
# - docker: Allow ps, build with safe paths
# - gh: Allow api with GET only
# - terraform: Allow fmt and plan only
# - terragrunt: Allow plan only
# - az: Allow list and show only
# - kubectl/k: Allow read-only operations

# docker ps - allow (read-only)
decisions[decision] if {
	input.parsed.executable == "docker"
	input.parsed.subcommand == "ps"
	decision := {"action": "allow"}
}

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
		"reason": "gh api requires explicit --method GET. Only GET requests are allowed for safety.",
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
		"reason": "Only GET method is allowed for gh api. POST, PUT, DELETE, and PATCH are not permitted.",
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
		"reason": "Only `terraform fmt` and `terraform plan` are allowed. Dangerous operations like apply, destroy, or init are not permitted.",
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
		"reason": "Only `terragrunt plan` is allowed. Dangerous operations like apply, destroy, or run-all are not permitted.",
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

# az --version / az version - allow (read-only)
az_is_version if {
	input.parsed.subcommand == null
	"--version" in input.parsed.flags
}

az_is_version if {
	input.parsed.subcommand == "version"
}

decisions[decision] if {
	input.parsed.executable == "az"
	az_is_version
	decision := {"action": "allow"}
}

# az repos pr create / az pipelines run - no decision: the user's own
# settings decide. Every other az write is denied below.
az_deferred_to_user if {
	input.parsed.subcommand == "repos"
	array.slice(input.parsed.arguments, 0, 2) == ["pr", "create"]
}

az_deferred_to_user if {
	input.parsed.subcommand == "pipelines"
	count(input.parsed.arguments) > 0
	input.parsed.arguments[0] == "run"
}

# az rest - allow GET only, same as gh api. With both --method and -m the
# later one wins, so neither is trusted and the request is denied below.
az_rest_method := lower(trim(input.parsed.options["--method"], "\"'")) if {
	not input.parsed.options["-m"]
}

az_rest_method := lower(trim(input.parsed.options["-m"], "\"'")) if {
	not input.parsed.options["--method"]
}

# az rest sends an Azure access token with the request (for --resource, or
# the one az infers from the URL), so a GET is only allowed to Azure itself:
# a relative ARM path or an Azure/Microsoft host. Anything else defers to the
# user, since a GET to another host could carry the token there.
az_rest_url := trim(input.parsed.options["--url"], "\"'")

az_rest_url := trim(input.parsed.options["--uri"], "\"'") if {
	not input.parsed.options["--url"]
}

# The host must end at a port, path, query or fragment: nothing like
# "https://attacker.example?.visualstudio.com" or "https://x.azure.com@attacker"
az_rest_azure_url_patterns := [
	`^https://(management\.azure\.com|dev\.azure\.com|vssps\.dev\.azure\.com|graph\.microsoft\.com)(:443)?([/?#].*)?$`,
	`^https://[A-Za-z0-9-]+\.visualstudio\.com(:443)?([/?#].*)?$`,
]

# Quotes, escapes or expansions inside the URL change what az receives:
# /""/attacker.example becomes //attacker.example in the shell
az_rest_url_has_shell_syntax if regex.match("[\"'\\\\$`]", az_rest_url)

# A relative ARM path; az prefixes the management endpoint
az_rest_url_is_azure if {
	not az_rest_url_has_shell_syntax
	startswith(az_rest_url, "/")
	not startswith(az_rest_url, "//")
}

az_rest_url_is_azure if {
	not az_rest_url_has_shell_syntax
	some pattern in az_rest_azure_url_patterns
	regex.match(pattern, lower(az_rest_url))
}

az_rest_output_file_safe if not input.parsed.options["--output-file"]

az_rest_output_file_safe if helpers.is_safe_path(input.parsed.options["--output-file"])

decisions[decision] if {
	input.parsed.executable == "az"
	input.parsed.subcommand == "rest"
	az_rest_method == "get"
	az_rest_url_is_azure
	az_rest_output_file_safe
	decision := {"action": "allow"}
}

decisions[decision] if {
	input.parsed.executable == "az"
	input.parsed.subcommand == "rest"
	not az_rest_method
	decision := {
		"action": "deny",
		"reason": "az rest requires an explicit --method GET. Only GET requests are allowed for safety.",
	}
}

decisions[decision] if {
	input.parsed.executable == "az"
	input.parsed.subcommand == "rest"
	az_rest_method != "get"
	decision := {
		"action": "deny",
		"reason": "Only GET is allowed for az rest. POST, PUT, PATCH and DELETE are not permitted.",
	}
}

# az other commands - deny
decisions[decision] if {
	input.parsed.executable == "az"
	not az_has_list
	not az_has_show
	not az_is_version
	not az_deferred_to_user
	input.parsed.subcommand != "rest"
	decision := {
		"action": "deny",
		"reason": "Only Azure CLI read-only commands with 'list' or 'show' are allowed. Dangerous operations like create, delete, update, or set are not permitted.",
	}
}

# kubectl/k read-only subcommands
kubectl_read_only_subcommands := ["get", "list", "describe", "logs", "top", "version", "api-versions", "api-resources", "explain", "cluster-info"]

# Helper: check if executable is kubectl or its alias
is_kube_exe if {
	input.parsed.executable == "kubectl"
}

is_kube_exe if {
	input.parsed.executable == "k"
}

# Helper: check if kube command is read-only allowed
kube_is_allowed if {
	is_kube_exe
	some subcommand in kubectl_read_only_subcommands
	input.parsed.subcommand == subcommand
}

kube_is_allowed if {
	is_kube_exe
	input.parsed.subcommand == "config"
	count(input.parsed.arguments) > 0
	input.parsed.arguments[0] == "view"
}

kube_is_allowed if {
	is_kube_exe
	input.parsed.subcommand == "auth"
	count(input.parsed.arguments) > 0
	input.parsed.arguments[0] == "can-i"
}

# kubectl/k read-only - allow
decisions[decision] if {
	is_kube_exe
	kube_is_allowed
	decision := {"action": "allow"}
}

# kubectl/k non-read-only - deny
decisions[decision] if {
	is_kube_exe
	not kube_is_allowed
	decision := {
		"action": "deny",
		"reason": "Only read-only kubectl operations are allowed",
	}
}
