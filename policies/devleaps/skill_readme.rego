package devleaps

import data.helpers.flags

# Guidance: README skill activation via file edit
guidances[g] if {
    input.file_path
    endswith(input.file_path, "README.md")
    not flags.is_set("skill_readme_activated")
    g := {
        "content": "Detected work on README. Skill readme-common and readme-devleaps MUST be activated.",
        "flags": [{
            "name": "skill_readme_activated"
        }]
    }
}
