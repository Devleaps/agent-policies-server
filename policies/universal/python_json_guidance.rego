package universal

# Guidance: suggest jq instead of python -c for JSON processing in bash
guidances[guidance] if {
	input.parsed.executable == "python"
	input.parsed.options["-c"]
	contains(input.parsed.options["-c"], "json")
	guidance := {"content": "Consider using `jq` instead of `python -c` for JSON processing in bash."}
}

guidances[guidance] if {
	input.parsed.executable == "python3"
	input.parsed.options["-c"]
	contains(input.parsed.options["-c"], "json")
	guidance := {"content": "Consider using `jq` instead of `python3 -c` for JSON processing in bash."}
}
