package demo_flags

import data.helpers.flags

# Test execution tracking: pytest sets flag for 100 invocations
decisions contains decision if {
	input.parsed.executable == "pytest"
	decision := {
		"action": "allow",
		"flags": [{
			"name": "ran_tests",
			"value": true,
			"expires_after": 100,
			"expires_unit": "invocations",
		}],
	}
}

# File edit invalidates test flag
decisions contains decision if {
	endswith(input.file_path, ".py")
	decision := {"flags": [{
		"name": "ran_tests",
		"value": false,
	}]}
}

# Commit requires tests
decisions contains decision if {
	input.parsed.executable == "git"
	input.parsed.subcommand == "commit"
	not flags.equals("ran_tests", true)
	decision := {
		"action": "deny",
		"reason": "Please run pytest before committing",
	}
}
