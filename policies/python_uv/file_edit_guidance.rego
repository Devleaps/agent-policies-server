package python_uv

# uv_pyproject - no measurement needed (unconditional message, gated purely
# on file path) - a plain guidances rule, not incomplete/require, since
# there's nothing to ask the client to compute.
guidances contains guidance if {
	endswith(input.file_path, "pyproject.toml")
	guidance := {"content": concat("", [
		"Consider using `uv add package-name` instead of editing pyproject.toml directly, ",
		"so uv can resolve and lock the dependency correctly.",
	])}
}
