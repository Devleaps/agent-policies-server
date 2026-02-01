package demo_flags

import data.helpers.flags

# Multi-step workflow: lint → test → deploy

# Step 1: Linting sets a flag
decisions[decision] if {
    input.parsed.executable == "ruff"
    input.parsed.subcommand == "check"
    decision := {
        "action": "allow",
        "flags": [
            {
                "name": "passed_lint",
                "value": true,
                "expires_after": 50,
                "expires_unit": "invocations"
            }
        ]
    }
}

# Step 2: Testing requires lint, sets test flag
decisions[decision] if {
    input.parsed.executable == "pytest"
    not flags.equals("passed_lint", true)
    decision := {
        "action": "deny",
        "reason": "Please run 'ruff check' before running tests"
    }
}

decisions[decision] if {
    input.parsed.executable == "pytest"
    flags.equals("passed_lint", true)
    decision := {
        "action": "allow",
        "flags": [
            {
                "name": "passed_tests",
                "value": true,
                "expires_after": 30,
                "expires_unit": "invocations"
            }
        ]
    }
}

# Step 3: Deploy requires both lint and tests
decisions[decision] if {
    input.parsed.executable == "docker"
    input.parsed.subcommand == "push"
    not flags.equals("passed_lint", true)
    decision := {
        "action": "deny",
        "reason": "Deploy requires lint check. Run 'ruff check' first."
    }
}

decisions[decision] if {
    input.parsed.executable == "docker"
    input.parsed.subcommand == "push"
    flags.equals("passed_lint", true)
    not flags.equals("passed_tests", true)
    decision := {
        "action": "deny",
        "reason": "Deploy requires passing tests. Run 'pytest' first."
    }
}

decisions[decision] if {
    input.parsed.executable == "docker"
    input.parsed.subcommand == "push"
    flags.equals("passed_lint", true)
    flags.equals("passed_tests", true)
    decision := {
        "action": "allow"
    }
}
