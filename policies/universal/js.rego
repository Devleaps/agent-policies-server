package universal

# JavaScript/Node.js command policies
# - npm: Allow common development commands
# - yarn: Allow common development commands
# - pnpm: Allow common development commands

# node inline evaluation flags
node_eval_options := {"-e", "--eval", "-p", "--print", "-pe"}

# node -e / -p - deny (arbitrary code execution)
decisions[decision] if {
	input.parsed.executable == "node"
	some key, _ in input.parsed.options
	key in node_eval_options
	decision := {
		"action": "deny",
		"reason": "By policy, inline code execution via `node -e` or `node -p` is not allowed. Place code in a script file or use the existing test framework instead.",
	}
}

decisions[decision] if {
	input.parsed.executable == "node"
	some flag in input.parsed.flags
	flag in node_eval_options
	decision := {
		"action": "deny",
		"reason": "By policy, inline code execution via `node -e` or `node -p` is not allowed. Place code in a script file or use the existing test framework instead.",
	}
}

# npm test - allow
decisions[decision] if {
	input.parsed.executable == "npm"
	input.parsed.subcommand == "test"
	decision := {"action": "allow"}
}

# npm run test - allow
decisions[decision] if {
	input.parsed.executable == "npm"
	input.parsed.subcommand == "run"
	count(input.parsed.arguments) > 0
	input.parsed.arguments[0] == "test"
	decision := {"action": "allow"}
}

# npm run build - allow
decisions[decision] if {
	input.parsed.executable == "npm"
	input.parsed.subcommand == "run"
	count(input.parsed.arguments) > 0
	input.parsed.arguments[0] == "build"
	decision := {"action": "allow"}
}

# yarn test - allow
decisions[decision] if {
	input.parsed.executable == "yarn"
	count(input.parsed.arguments) > 0
	input.parsed.arguments[0] == "test"
	decision := {"action": "allow"}
}

# yarn start - allow
decisions[decision] if {
	input.parsed.executable == "yarn"
	count(input.parsed.arguments) > 0
	input.parsed.arguments[0] == "start"
	decision := {"action": "allow"}
}

# yarn build - allow
decisions[decision] if {
	input.parsed.executable == "yarn"
	count(input.parsed.arguments) > 0
	input.parsed.arguments[0] == "build"
	decision := {"action": "allow"}
}

# yarn remove - allow
decisions[decision] if {
	input.parsed.executable == "yarn"
	count(input.parsed.arguments) > 0
	input.parsed.arguments[0] == "remove"
	decision := {"action": "allow"}
}

# yarn why - allow
decisions[decision] if {
	input.parsed.executable == "yarn"
	count(input.parsed.arguments) > 0
	input.parsed.arguments[0] == "why"
	decision := {"action": "allow"}
}

# pnpm build - allow
decisions[decision] if {
	input.parsed.executable == "pnpm"
	count(input.parsed.arguments) > 0
	input.parsed.arguments[0] == "build"
	decision := {"action": "allow"}
}
