package universal

# uvx command policies
# - Allow whitelisted tools (black, mypy, bandit, ruff)

# Whitelisted uvx tools
uvx_allowed_tools := ["black", "mypy", "bandit", "ruff"]

# Allow whitelisted uvx tools
decisions[decision] if {
	input.parsed.executable == "uvx"
	count(input.parsed.arguments) > 0
	input.parsed.arguments[0] in uvx_allowed_tools
	decision := {"action": "allow"}
}
