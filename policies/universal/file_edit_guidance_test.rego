package universal

# comment_ratio

test_comment_ratio_pass1_incomplete_for_py_file if {
	decisions[{"action": "incomplete", "require": [{"kind": "comment_ratio"}]}] with input as {"file_path": "src/app.py"}
}

test_comment_ratio_not_requested_for_non_py_file if {
	not decisions[{"action": "incomplete", "require": [{"kind": "comment_ratio"}]}]
		with input as {"file_path": "src/app.js"}
}

test_comment_ratio_guidance_fires_above_threshold if {
	expected := concat("", [
		"This file is 60% comments. ",
		"Consider whether this much commentary is necessary, or whether the code itself could be made clearer.",
	])
	guidances[{"content": expected}] with input as {
		"file_path": "src/app.py",
		"measurements": {"comment_ratio": {"ratio": 0.6}},
	}
}

test_comment_ratio_guidance_does_not_fire_at_or_below_threshold if {
	count(guidances) == 0 with input as {
		"file_path": "src/app.py",
		"measurements": {"comment_ratio": {"ratio": 0.4}},
	}
}

# comment_overlap

test_comment_overlap_pass1_incomplete_for_py_file if {
	decisions[{"action": "incomplete", "require": [{"kind": "comment_overlap"}]}] with input as {"file_path": "src/app.py"}
}

test_comment_overlap_not_requested_for_init_py if {
	not decisions[{"action": "incomplete", "require": [{"kind": "comment_overlap"}]}]
		with input as {"file_path": "src/__init__.py"}
}

test_comment_overlap_guidance_fires_at_or_above_threshold if {
	guidances[{"content": "Ensure comments add value beyond describing what's obvious from the code."}] with input as {
		"file_path": "src/app.py",
		"measurements": {"comment_overlap": {"ratio": 0.4}},
	}
}

test_comment_overlap_guidance_does_not_fire_below_threshold if {
	count(guidances) == 0 with input as {
		"file_path": "src/app.py",
		"measurements": {"comment_overlap": {"ratio": 0.39}},
	}
}

# commented_code

test_commented_code_pass1_incomplete_for_py_file if {
	decisions[{"action": "incomplete", "require": [{"kind": "commented_code"}]}] with input as {"file_path": "src/app.py"}
}

test_commented_code_guidance_fires_at_or_above_threshold if {
	expected := concat("", [
		"If a large segment of code was commented out within a Git project, ",
		"it should be removed rather than maintained for historical purposes.",
	])
	guidances[{"content": expected}] with input as {
		"file_path": "src/app.py",
		"measurements": {"commented_code": {"max_run": 2}},
	}
}

test_commented_code_guidance_does_not_fire_below_threshold if {
	count(guidances) == 0 with input as {
		"file_path": "src/app.py",
		"measurements": {"commented_code": {"max_run": 1}},
	}
}

# legacy_code

test_legacy_code_pass1_incomplete_for_py_file if {
	decisions[{"action": "incomplete", "require": [{"kind": "legacy_code"}]}] with input as {"file_path": "src/app.py"}
}

test_legacy_code_guidance_fires_when_matched if {
	expected := concat("", [
		"Is backwards compatibility actually a requirement here? ",
		"If it was not explicitly requested, check with the user before adding it.",
	])
	guidances[{"content": expected}] with input as {
		"file_path": "src/app.py",
		"measurements": {"legacy_code": {"matched": true}},
	}
}

test_legacy_code_guidance_does_not_fire_when_not_matched if {
	count(guidances) == 0 with input as {
		"file_path": "src/app.py",
		"measurements": {"legacy_code": {"matched": false}},
	}
}

# mid_code_import

test_mid_code_import_pass1_incomplete_for_py_file if {
	decisions[{"action": "incomplete", "require": [{"kind": "mid_code_import"}]}] with input as {"file_path": "src/app.py"}
}

test_mid_code_import_guidance_fires_when_matched if {
	expected := concat("", [
		"Move imports to module level unless there's a specific reason for a nested import ",
		"(e.g. avoiding circular dependencies or expensive imports).",
	])
	guidances[{"content": expected}] with input as {
		"file_path": "src/app.py",
		"measurements": {"mid_code_import": {"matched": true}},
	}
}

test_mid_code_import_guidance_does_not_fire_when_not_matched if {
	count(guidances) == 0 with input as {
		"file_path": "src/app.py",
		"measurements": {"mid_code_import": {"matched": false}},
	}
}

# license (README.md only)

test_license_pass1_incomplete_for_readme if {
	decisions[{"action": "incomplete", "require": [{"kind": "license"}]}] with input as {"file_path": "README.md"}
}

test_license_not_requested_for_py_file if {
	not decisions[{"action": "incomplete", "require": [{"kind": "license"}]}] with input as {"file_path": "src/app.py"}
}

test_license_guidance_fires_when_matched if {
	expected := concat("", [
		"An AI agent may only add a License section with explicit user permission ",
		"and a user-selected license.",
	])
	guidances[{"content": expected}] with input as {
		"file_path": "README.md",
		"measurements": {"license": {"matched": true}},
	}
}

test_license_guidance_does_not_fire_when_not_matched if {
	count(guidances) == 0 with input as {
		"file_path": "README.md",
		"measurements": {"license": {"matched": false}},
	}
}

# Once every measurement is present, no check should still ask for more -
# guards against a stale `not input.measurements.X` condition.
test_py_file_with_all_measurements_present_asks_for_nothing_more if {
	full_input := {
		"file_path": "src/app.py",
		"measurements": {
			"comment_ratio": {"ratio": 0.1},
			"comment_overlap": {"ratio": 0.1},
			"commented_code": {"max_run": 0},
			"legacy_code": {"matched": false},
			"mid_code_import": {"matched": false},
		},
	}
	not decisions[{"action": "incomplete", "require": [{"kind": "comment_ratio"}]}] with input as full_input
	not decisions[{"action": "incomplete", "require": [{"kind": "comment_overlap"}]}] with input as full_input
	not decisions[{"action": "incomplete", "require": [{"kind": "commented_code"}]}] with input as full_input
	not decisions[{"action": "incomplete", "require": [{"kind": "legacy_code"}]}] with input as full_input
	not decisions[{"action": "incomplete", "require": [{"kind": "mid_code_import"}]}] with input as full_input
}
