package universal

# source command policies
# - Allow source venv/bin/activate (virtual environment activation)
# The sourced file itself must be the activate script: the text appearing
# elsewhere in the command (source x && echo venv/bin/activate) is not enough.

source_activate_scripts := {
	"venv/bin/activate",
	".venv/bin/activate",
	"./venv/bin/activate",
	"./.venv/bin/activate",
}

decisions[decision] if {
	input.parsed.executable == "source"
	count(input.parsed.arguments) == 1
	script := input.parsed.arguments[0]
	script in source_activate_scripts
	count(input.parsed.flags) == 0
	count(input.parsed.options) == 0
	count(input.parsed.redirects) == 0
	decision := {"action": "allow"}
}
