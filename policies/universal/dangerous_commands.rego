package universal

# Dangerous commands that are always blocked for security reasons

# Block sudo - privilege escalation risk
decisions[decision] if {
	input.parsed.executable == "sudo"
	decision := {
		"action": "deny",
		"reason": "By policy, sudo commands are not allowed for security reasons. Run commands without sudo privileges or configure appropriate permissions.",
	}
}

# Block kill - use pkill instead
decisions[decision] if {
	input.parsed.executable == "kill"
	decision := {
		"action": "deny",
		"reason": "By policy, kill commands are not allowed. Use pkill instead for safer process termination (e.g., pkill -f processname).",
	}
}

# Block killall - use pkill instead
decisions[decision] if {
	input.parsed.executable == "killall"
	decision := {
		"action": "deny",
		"reason": "By policy, killall commands are not allowed. Use pkill instead for safer process termination (e.g., pkill -f processname).",
	}
}

# Block xargs - can bypass policy controls
decisions[decision] if {
	input.parsed.executable == "xargs"
	decision := {
		"action": "deny",
		"reason": "By policy, xargs is not allowed. xargs can execute arbitrary commands and bypass policy controls.",
	}
}

# Block perl - can execute arbitrary code
decisions[decision] if {
	input.parsed.executable == "perl"
	decision := {
		"action": "deny",
		"reason": "By policy, perl is not allowed. Perl can execute arbitrary code (e.g., perl -e) and bypass policy controls.",
	}
}

# Block timeout - can wrap arbitrary commands
decisions[decision] if {
	input.parsed.executable == "timeout"
	decision := {
		"action": "deny",
		"reason": "By policy, timeout commands are not allowed. Timeout can be used to wrap arbitrary commands and bypass policy controls.",
	}
}

# Block time - can wrap arbitrary commands
decisions[decision] if {
	input.parsed.executable == "time"
	decision := {
		"action": "deny",
		"reason": "By policy, time commands are not allowed. Time can be used to wrap arbitrary commands and bypass policy controls.",
	}
}

# Block awk - security risk
decisions[decision] if {
	input.parsed.executable == "awk"
	decision := {
		"action": "deny",
		"reason": "By policy, awk commands are not allowed for security reasons.",
	}
}

# Sleep duration limit - deny if > 60 seconds
decisions[decision] if {
	input.parsed.executable == "sleep"
	count(input.parsed.arguments) > 0
	duration := to_number(input.parsed.arguments[0])
	duration > 60
	decision := {
		"action": "deny",
		"reason": sprintf("Sleep duration %v exceeds maximum 60 seconds", [duration]),
	}
}

# Sleep - allow if <= 60 seconds
decisions[decision] if {
	input.parsed.executable == "sleep"
	count(input.parsed.arguments) > 0
	duration := to_number(input.parsed.arguments[0])
	duration <= 60
	decision := {"action": "allow"}
}
