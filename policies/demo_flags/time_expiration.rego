package demo_flags

import data.helpers.flags

# Time-based expiration example: Build cache valid for 2 seconds (for fast testing)

decisions[decision] if {
    input.parsed.executable == "docker"
    input.parsed.subcommand == "build"
    decision := {
        "action": "allow",
        "flags": [
            {
                "name": "build_cached",
                "value": true,
                "expires_after": 2,
                "expires_unit": "seconds"
            }
        ]
    }
}

# Docker push can skip rebuild if build is cached
decisions[decision] if {
    input.parsed.executable == "docker"
    input.parsed.subcommand == "push"
    not flags.equals("build_cached", true)
    decision := {
        "action": "ask",
        "reason": "No recent build found. Run 'docker build' first?"
    }
}

decisions[decision] if {
    input.parsed.executable == "docker"
    input.parsed.subcommand == "push"
    flags.equals("build_cached", true)
    decision := {
        "action": "allow"
    }
}

# Immediate expiration example (expires_after: 0)
decisions[decision] if {
    input.parsed.executable == "echo"
    count(input.parsed.arguments) > 0
    input.parsed.arguments[0] == "one-time"
    decision := {
        "action": "allow",
        "flags": [
            {
                "name": "echo_fired",
                "expires_after": 0,
                "expires_unit": "invocations"
            }
        ]
    }
}

# This will never see the flag because it expires immediately
decisions[decision] if {
    flags.is_set("echo_fired")
    decision := {
        "action": "deny",
        "reason": "This should never fire"
    }
}
