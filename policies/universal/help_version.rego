package universal

# --help / --version for known executables
# - <cmd> --help, <cmd> --version: allowed for every known executable
# - <cmd> <subcommand> --help: allowed only for tools whose subcommands are
#   built in, and only when the subcommand looks like one (no / or .)
# - No other flags, options or positional arguments
#
# Deliberately absent: npx and uvx (download and run packages), pytest
# (--help loads the project's conftest.py). Interpreters and tools that treat
# an unknown subcommand as a script (python, node, yarn, pnpm) get no
# positional at all, so "node script --help" never runs a script.
# -h is not included: for du, df, sort and ls it means something else.

help_version_flags := {"--help", "--version"}

help_subcommand_tools := {
	"git", "docker", "podman", "kubectl", "terraform", "terragrunt", "gh",
	"az", "gcloud", "aws", "npm", "uv", "pip", "pip3", "cargo", "go",
	"brew", "opa", "regal", "vale", "ruff", "helm", "tflint",
}

help_plain_tools := {
	"python", "python3", "node", "yarn", "pnpm", "black", "mypy", "bandit",
	"jq", "yq", "curl", "sqlite3", "trash", "rg", "fd", "gofmt", "rustc",
	"java", "javac", "deno", "bun", "make", "cmake", "shellcheck",
}

help_positionals := array.concat([input.parsed.subcommand], input.parsed.arguments) if {
	input.parsed.subcommand != null
}

help_positionals := input.parsed.arguments if {
	input.parsed.subcommand == null
}

help_only_flag if {
	count(input.parsed.flags) == 1
	input.parsed.flags[0] in help_version_flags
	count(input.parsed.options) == 0
}

help_positionals_allowed if {
	count(help_positionals) == 0
	input.parsed.executable in help_subcommand_tools
}

help_positionals_allowed if {
	count(help_positionals) == 0
	input.parsed.executable in help_plain_tools
}

help_positionals_allowed if {
	count(help_positionals) == 1
	input.parsed.executable in help_subcommand_tools
	word := help_positionals[0]
	not contains(word, "/")
	not contains(word, ".")
}

# Also used to exempt help requests from catch-all denies (e.g. terraform)
help_request if {
	help_only_flag
	help_positionals_allowed
}

decisions[decision] if {
	help_request
	decision := {"action": "allow"}
}
