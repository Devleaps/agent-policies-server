package python_uv

test_uv_pyproject_guidance_fires_for_pyproject_toml if {
	expected := concat("", [
		"Consider using `uv add package-name` instead of editing pyproject.toml directly, ",
		"so uv can resolve and lock the dependency correctly.",
	])
	guidances[{"content": expected}] with input as {"file_path": "pyproject.toml"}
}

test_uv_pyproject_guidance_does_not_fire_for_other_files if {
	count(guidances) == 0 with input as {"file_path": "src/app.py"}
}
