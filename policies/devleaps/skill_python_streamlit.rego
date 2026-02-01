package devleaps

import data.helpers.flags

# Guidance: Streamlit skill activation via direct executable
guidances[g] if {
    input.parsed.executable == "streamlit"
    not flags.is_set("skill_python_streamlit_activated")
    g := {
        "content": "Detected work on Streamlit. Agents with skill support are requested to activate skill python-streamlit-common and python-streamlit-devleaps.",
        "flags": [{
            "name": "skill_python_streamlit_activated",
            "expires_after": 200,
            "expires_unit": "invocations"
        }]
    }
}

# Guidance: Streamlit skill activation via uv run streamlit
guidances[g] if {
    input.parsed.executable == "uv"
    input.parsed.subcommand == "run"
    count(input.parsed.arguments) > 0
    input.parsed.arguments[0] == "streamlit"
    not flags.is_set("skill_python_streamlit_activated")
    g := {
        "content": "Detected work on Streamlit. Agents with skill support are requested to activate skill python-streamlit-common and python-streamlit-devleaps.",
        "flags": [{
            "name": "skill_python_streamlit_activated",
            "expires_after": 200,
            "expires_unit": "invocations"
        }]
    }
}
