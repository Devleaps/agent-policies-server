package devleaps

import data.helpers.flags

# Executables that indicate FastAPI work
fastapi_executables := {"uvicorn", "fastapi"}

# Guidance: FastAPI skill activation via direct executable
guidances[g] if {
    fastapi_executables[input.parsed.executable]
    not flags.is_set("skill_python_fastapi_activated")
    g := {
        "content": "Detected work on FastAPI. Skill python-fastapi-common and python-fastapi-devleaps MUST be activated.",
        "flags": [{
            "name": "skill_python_fastapi_activated"
        }]
    }
}

# Guidance: FastAPI skill activation via uv run uvicorn / uv run fastapi
guidances[g] if {
    input.parsed.executable == "uv"
    input.parsed.subcommand == "run"
    count(input.parsed.arguments) > 0
    fastapi_executables[input.parsed.arguments[0]]
    not flags.is_set("skill_python_fastapi_activated")
    g := {
        "content": "Detected work on FastAPI. Skill python-fastapi-common and python-fastapi-devleaps MUST be activated.",
        "flags": [{
            "name": "skill_python_fastapi_activated"
        }]
    }
}
