"""Python UV bundle - UV-specific policies using shared whitelist."""

from src.python_uv.uv_python_deny import (
    uv_python_direct_deny_rule,
    uv_python_run_escape_deny_rule,
)
from src.python_uv.uv_pip_deny import (
    uv_pip_direct_deny_rule,
    uv_pip_run_deny_rule,
)
from src.python_uv.uv_pip_install_guidance import uv_pip_install_deny_rule
from src.python_uv.uv_add_deny import uv_add_deny_rule
from src.python_uv.uv_venv_deny import uv_venv_deny_rule
from src.python_uv.uv_requirements_deny import uv_requirements_txt_deny_rule
from src.python_uv.uv_tools_deny import uv_tools_direct_deny_rule
from src.python_uv.uv_tools_allow import (
    uv_sync_allow_rule,
    uv_tools_run_allow_rule,
    uv_pytest_allow_rule,
)
from src.python_uv.uv_pyproject_guidance import uv_pyproject_guidance_rule

all_rules = [
    uv_python_direct_deny_rule,
    uv_python_run_escape_deny_rule,
    uv_pip_direct_deny_rule,
    uv_pip_run_deny_rule,
    uv_pip_install_deny_rule,
    uv_add_deny_rule,
    uv_venv_deny_rule,
    uv_requirements_txt_deny_rule,
    uv_tools_direct_deny_rule,
    uv_sync_allow_rule,
    uv_pytest_allow_rule,
    uv_tools_run_allow_rule,
]

all_post_file_edit_rules = [uv_pyproject_guidance_rule]

all_middleware = []

__all__ = ["all_rules", "all_middleware", "all_post_file_edit_rules"]
