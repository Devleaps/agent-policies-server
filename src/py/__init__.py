"""Python ecosystem policies (pip, pytest, python, python3, virtualenv, tools)."""

from src.py.pip_install_requirements import pip_install_requirements_rule
from src.py.pip_freeze import pip_freeze_rule, requirements_rule
from src.py.pip_uninstall import pip_uninstall_rule
from src.py.pip_install_packages import pip_install_packages_rule
from src.py.pip_show import pip_show_rule
from src.py.pip_audit_policy import pip_audit_rule
from src.py.python_script import python_script_rule
from src.py.python_module import python_module_rule
from src.py.python_test_file import python_test_file_rule
from src.py.python3_venv import python3_venv_rule
from src.py.black_policy import black_format_rule
from src.py.ruff_policy import ruff_check_rule, ruff_format_rule
from src.py.mypy_policy import mypy_check_rule
from src.py.pytest_cov_policy import pytest_cov_rule
from src.py.comment_ratio_guidance import comment_ratio_guidance_rule
from src.py.comment_overlap_guidance import comment_overlap_guidance_rule

# Middleware
from src.py.uv_middleware import all_middleware as uv_middleware

all_rules = [
    pip_install_requirements_rule,
    pip_freeze_rule,
    pip_uninstall_rule,
    pip_install_packages_rule,
    pip_show_rule,
    pip_audit_rule,
    requirements_rule,
    python_script_rule,
    python_module_rule,
    python_test_file_rule,
    python3_venv_rule,
    black_format_rule,
    ruff_check_rule,
    ruff_format_rule,
    mypy_check_rule,
    pytest_cov_rule
]

# PostFileEditEvent handlers for Python-specific guidance
all_post_file_edit_rules = [
    comment_ratio_guidance_rule,
    comment_overlap_guidance_rule
]

all_middleware = [
    *uv_middleware
]