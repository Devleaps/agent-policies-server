package universal

# Small read-only utilities
# - date: display only, never set the clock
# - dig: DNS lookups
# - md5: checksums (safe paths required)
# - pgrep: list processes, with a pointer to pkill

# date - allow displaying the date, never setting it
# Setting the clock takes a bare operand (macOS) or -s/--set (GNU); display
# formats always start with "+". The parser reads "-u +%Y" as option -u with
# value "+%Y", so boolean flags may carry a format as their value.
date_flag_keys := {"-u", "--utc", "-R", "-I"}

date_value_keys := {"-d", "--date"}

# A display format: +%Y, or quoted as the parser keeps it ('+%Y %H')
date_is_format(word) if startswith(trim_left(word, "\"'"), "+")

date_flag_is_display(flag) if {
	flag in date_flag_keys
}

# macOS -v adjustments arrive glued to their value (e.g. "-v-1d")
date_flag_is_display(flag) if {
	startswith(flag, "-v")
}

date_option_is_display(key, value) if {
	key in date_flag_keys
	date_is_format(value)
}

date_option_is_display(key, _) if {
	key in date_value_keys
}

date_option_is_display(key, _) if {
	startswith(key, "-v")
}

decisions[decision] if {
	input.parsed.executable == "date"
	every flag in input.parsed.flags {
		date_flag_is_display(flag)
	}
	every key, value in input.parsed.options {
		date_option_is_display(key, value)
	}
	every arg in input.parsed.arguments {
		date_is_format(arg)
	}
	decision := {"action": "allow"}
}

# dig - DNS lookup (read-only), same as nslookup
decisions[decision] if {
	input.parsed.executable == "dig"
	decision := {"action": "allow"}
}

# md5 - checksum files (safe paths required). The parser keeps one value per
# option, so a repeated option (md5 -q /etc/passwd -q x) hides a file; md5
# only allows when no option occurs twice in the command
md5_repeated_option if {
	some key, _ in input.parsed.options
	pattern := concat("", [`(^|\s)`, key, `(\s|=|$)`])
	count(regex.find_n(pattern, input.parsed.original, -1)) > 1
}

md5_allowed if {
	all_args_and_options_safe
	not md5_repeated_option
}

decisions[decision] if {
	input.parsed.executable == "md5"
	md5_allowed
	decision := {"action": "allow"}
}

decisions[decision] if {
	input.parsed.executable == "md5"
	not all_args_and_options_safe
	decision := {
		"action": "deny",
		"reason": "md5: only workspace-relative paths are allowed (no absolute paths, no ../, no /tmp)",
	}
}

# pgrep - list matching processes (read-only)
decisions[decision] if {
	input.parsed.executable == "pgrep"
	decision := {"action": "allow"}
}

guidances[guidance] if {
	input.parsed.executable == "pgrep"
	guidance := {"content": "To stop the processes pgrep matches, use pkill with the same pattern (e.g., pkill -f processname) rather than kill with the listed PIDs."}
}
