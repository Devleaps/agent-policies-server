package universal

# source command policies
# - Allow source venv/bin/activate (virtual environment activation)

decisions[decision] if {
	input.parsed.executable == "source"
	contains(input.event.command, "venv/bin/activate")
	decision := {"action": "allow"}
}
