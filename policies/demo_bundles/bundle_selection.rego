package demo_bundles

import data.helpers.bundles

# Enforce that at least one Python package manager bundle is active.
# If neither python_pip nor python_uv is enabled, deny any tool use
# with an explanatory message asking the user to choose one.

decisions[decision] if {
    not bundles.is_active("python_pip")
    not bundles.is_active("python_uv")
    decision := {
        "action": "deny",
        "reason": "No Python package manager bundle is active. Before using any tool, please choose one: enable 'python_pip' (for pip-based projects) or 'python_uv' (for uv-based projects)."
    }
}
