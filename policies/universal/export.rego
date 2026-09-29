package universal

# export - allow setting variables
# - Every argument must be NAME=value
# - All variable names are allowed for now
# - Any value: $X only copies a variable, and a $(cmd) in it is either
#   evaluated as a command of its own or rejected by the parser

export_assignment(arg) if {
	regex.match("^[A-Za-z_][A-Za-z0-9_]*=", arg)
}

decisions[decision] if {
	input.parsed.executable == "export"
	count(input.parsed.arguments) > 0
	count(input.parsed.flags) == 0
	count(input.parsed.options) == 0
	every arg in input.parsed.arguments {
		export_assignment(arg)
	}
	decision := {"action": "allow"}
}
