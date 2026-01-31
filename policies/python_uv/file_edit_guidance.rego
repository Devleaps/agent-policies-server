package python_uv

# UV-specific guidance (inherits universal Python guidance)
guidance_activations[check] if {
	endswith(input.file_path, "pyproject.toml")
	check := "uv_pyproject"
}
