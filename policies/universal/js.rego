package universal

# JavaScript/Node.js command policies
# - yarn: Allow common development commands

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
