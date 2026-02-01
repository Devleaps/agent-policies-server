package demo_flags

import data.helpers.flags

# Cooldown pattern: deny once with warning, then allow for 10 invocations
decisions[decision] if {
    input.parsed.executable == "gh"
    input.parsed.subcommand == "pr"
    count(input.parsed.arguments) >= 1
    input.parsed.arguments[0] == "create"
    not flags.is_set("pr_template_cooldown")
    decision := {
        "action": "deny",
        "reason": "Please check .github/PULL_REQUEST_TEMPLATE.md. We trust you to make the right decision.",
        "flags": [
            {
                "name": "pr_template_cooldown",
                "expires_after": 10,
                "expires_unit": "invocations"
            }
        ]
    }
}

# Subsequent gh pr create attempts allowed while cooldown active (no deny fires)
