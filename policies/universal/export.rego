package universal

# export - allow setting variables to literal values
# - Every argument must be NAME=value with no $ expansion or backticks
# - All variable names are allowed for now
# - export A=$(cmd) fails to parse and defers to the user

export_literal_assignment(arg) if {
	regex.match("^[A-Za-z_][A-Za-z0-9_]*=[^$`]*$", arg)
}

decisions[decision] if {
	input.parsed.executable == "export"
	count(input.parsed.arguments) > 0
	count(input.parsed.flags) == 0
	count(input.parsed.options) == 0
	every arg in input.parsed.arguments {
		export_literal_assignment(arg)
	}
	decision := {"action": "allow"}
}
