package universal

# JavaScript/Node.js command policies
# - npm: Allow common development commands
# - yarn: Allow common development commands
# - pnpm: Allow common development commands

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
