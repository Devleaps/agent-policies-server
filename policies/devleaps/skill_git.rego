package devleaps

import data.helpers.flags

# Git write operations that trigger skill activation
git_write_operations := {"add", "commit", "push", "mv", "init"}

# Guidance: Git skill activation for write operations
guidances[g] if {
    input.parsed.executable == "git"
    git_write_operations[input.parsed.subcommand]
    not flags.is_set("skill_git_activated")
    g := {
        "content": "Detected git write operation. Skill git-devleaps MUST be activated.",
        "flags": [{
            "name": "skill_git_activated"
        }]
    }
}

# Guidance: Git skill activation for branch creation/modification
# (git branch with arguments means creating/renaming, not just listing)
guidances[g] if {
    input.parsed.executable == "git"
    input.parsed.subcommand == "branch"
    count(input.parsed.arguments) > 0
    not flags.is_set("skill_git_activated")
    g := {
        "content": "Detected git write operation. Skill git-devleaps MUST be activated.",
        "flags": [{
            "name": "skill_git_activated"
        }]
    }
}

# Guidance: Git skill activation for branch rename (-m option)
guidances[g] if {
    input.parsed.executable == "git"
    input.parsed.subcommand == "branch"
    input.parsed.options["-m"]
    not flags.is_set("skill_git_activated")
    g := {
        "content": "Detected git write operation. Skill git-devleaps MUST be activated.",
        "flags": [{
            "name": "skill_git_activated"
        }]
    }
}
