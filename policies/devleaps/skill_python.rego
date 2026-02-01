package devleaps

import data.helpers.flags

# Python executables that trigger skill activation
python_executables := {"python", "python3", "uv", "pip", "pytest", "ruff", "mypy", "black"}

# Guidance: Python skill activation
guidances[g] if {
    python_executables[input.parsed.executable]
    not flags.is_set("skill_python_activated")
    g := {
        "content": "Detected work on Python. Agents with skill support are requested to activate skill python-common and python-devleaps.",
        "flags": [{
            "name": "skill_python_activated",
            "expires_after": 200,
            "expires_unit": "invocations"
        }]
    }
}
