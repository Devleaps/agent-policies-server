package universal

# cd command policies
# - Allow cd to any directory: cd itself reads and writes nothing
# - The protection is on what follows: later commands in the same chain are
#   evaluated from the cd target, so after leaving the workspace their
#   relative paths are no longer workspace-relative (see Location in
#   src/evaluation/rego.py)

decisions[decision] if {
	input.parsed.executable == "cd"
	decision := {"action": "allow"}
}
