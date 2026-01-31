package universal

# Python file guidance
guidance_activations[check] if {
	endswith(input.file_path, ".py")
	check := "comment_ratio"
}

guidance_activations[check] if {
	endswith(input.file_path, ".py")
	not endswith(input.file_path, "__init__.py")
	check := "comment_overlap"
}

guidance_activations[check] if {
	endswith(input.file_path, ".py")
	check := "commented_code"
}

guidance_activations[check] if {
	endswith(input.file_path, ".py")
	check := "legacy_code"
}

guidance_activations[check] if {
	endswith(input.file_path, ".py")
	check := "mid_code_import"
}

# README guidance
guidance_activations[check] if {
	endswith(input.file_path, "README.md")
	check := "license"
}
