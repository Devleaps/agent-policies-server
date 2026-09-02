package universal

# File-edit guidance via the same incomplete/require multi-pass protocol
# used by python_pip/pip_install.rego for PyPI age checks: a decision can
# say "I need a measurement" instead of committing to a verdict. Here the
# measurement is a structural fact about the file edit (comment-to-code
# ratio, overlap between a comment and its code, etc.), computed client-side
# against `structured_patch` and folded back into `input.measurements`
# keyed by check name. Rego owns every threshold; the client only computes
# raw facts (see src/measurements/*.js), never verdicts.

# comment_ratio - .py files, ratio of comment lines to all non-blank lines.
decisions contains decision if {
	endswith(input.file_path, ".py")
	not input.measurements.comment_ratio
	decision := {"action": "incomplete", "require": [{"kind": "comment_ratio"}]}
}

# comment_overlap - .py files (excluding __init__.py), a comment whose words
# mostly restate the code next to it should be removed, not kept.
decisions contains decision if {
	endswith(input.file_path, ".py")
	not endswith(input.file_path, "__init__.py")
	not input.measurements.comment_overlap
	decision := {"action": "incomplete", "require": [{"kind": "comment_overlap"}]}
}

# commented_code - .py files, 2+ consecutive commented-out lines.
decisions contains decision if {
	endswith(input.file_path, ".py")
	not input.measurements.commented_code
	decision := {"action": "incomplete", "require": [{"kind": "commented_code"}]}
}

# legacy_code - .py files, mentions of legacy/deprecated/backwards
# compatibility that may not actually be required.
decisions contains decision if {
	endswith(input.file_path, ".py")
	not input.measurements.legacy_code
	decision := {"action": "incomplete", "require": [{"kind": "legacy_code"}]}
}

# mid_code_import - .py files, an import statement nested below module
# level (not a blank/comment line at column 0).
decisions contains decision if {
	endswith(input.file_path, ".py")
	not input.measurements.mid_code_import
	decision := {"action": "incomplete", "require": [{"kind": "mid_code_import"}]}
}

# license - README.md files, any added line mentioning "license".
decisions contains decision if {
	endswith(input.file_path, "README.md")
	not input.measurements.license
	decision := {"action": "incomplete", "require": [{"kind": "license"}]}
}

guidances contains guidance if {
	input.measurements.comment_ratio.ratio > 0.4
	guidance := {"content": sprintf(
		concat("", [
			"This file is %v%% comments. ",
			"Consider whether this much commentary is necessary, or whether the code itself could be made clearer.",
		]),
		[round(input.measurements.comment_ratio.ratio * 100)],
	)}
}

guidances contains guidance if {
	input.measurements.comment_overlap.ratio >= 0.4
	guidance := {"content": "Ensure comments add value beyond describing what's obvious from the code."}
}

guidances contains guidance if {
	input.measurements.commented_code.max_run >= 2
	guidance := {"content": concat("", [
		"If a large segment of code was commented out within a Git project, ",
		"it should be removed rather than maintained for historical purposes.",
	])}
}

guidances contains guidance if {
	input.measurements.legacy_code.matched
	guidance := {"content": concat("", [
		"Is backwards compatibility actually a requirement here? ",
		"If it was not explicitly requested, check with the user before adding it.",
	])}
}

guidances contains guidance if {
	input.measurements.mid_code_import.matched
	guidance := {"content": concat("", [
		"Move imports to module level unless there's a specific reason for a nested import ",
		"(e.g. avoiding circular dependencies or expensive imports).",
	])}
}

guidances contains guidance if {
	input.measurements.license.matched
	guidance := {"content": concat("", [
		"An AI agent may only add a License section with explicit user permission ",
		"and a user-selected license.",
	])}
}
