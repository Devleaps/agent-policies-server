package universal

# Homebrew command policies
# - Allow read-only commands: info, uses, cat

# brew info - show package information (read-only)
decisions[decision] if {
	input.parsed.executable == "brew"
	count(input.parsed.arguments) > 0
	input.parsed.arguments[0] == "info"
	decision := {"action": "allow"}
}

# brew uses - show packages that depend on a formula (read-only)
decisions[decision] if {
	input.parsed.executable == "brew"
	count(input.parsed.arguments) > 0
	input.parsed.arguments[0] == "uses"
	decision := {"action": "allow"}
}

# brew cat - display formula file (read-only)
decisions[decision] if {
	input.parsed.executable == "brew"
	count(input.parsed.arguments) > 0
	input.parsed.arguments[0] == "cat"
	decision := {"action": "allow"}
}
