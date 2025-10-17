"""Python PIP bundle - Pip-specific and direct-execution policies using shared whitelist."""

from src.python_pip.pip_direct_deny import pip_direct_deny_rule
from src.python_pip.pip_install_whitelist import pip_install_whitelist_rule
from src.python_pip.pip_install_requirements import pip_install_requirements_rule
from src.python_pip.pip_freeze import pip_freeze_rule, requirements_rule
from src.python_pip.pip_uninstall import pip_uninstall_rule
from src.python_pip.pip_show import pip_show_rule
from src.python_pip.pip_audit_policy import pip_audit_rule
from src.python_pip.python3_venv import python3_venv_rule
from src.python_pip.python_script import python_script_rule
from src.python_pip.python_module import python_module_rule
from src.python_pip.python_test_file import python_test_file_rule
from src.python_pip.black_policy import black_format_rule
from src.python_pip.ruff_policy import ruff_check_rule, ruff_format_rule
from src.python_pip.mypy_policy import mypy_check_rule
from src.python_pip.pytest_cov_policy import pytest_cov_rule

all_rules = [
    pip_direct_deny_rule,
    pip_install_whitelist_rule,
    pip_install_requirements_rule,
    pip_freeze_rule,
    pip_uninstall_rule,
    pip_show_rule,
    pip_audit_rule,
    requirements_rule,
    python3_venv_rule,
    python_script_rule,
    python_module_rule,
    python_test_file_rule,
    black_format_rule,
    ruff_check_rule,
    ruff_format_rule,
    mypy_check_rule,
    pytest_cov_rule,
]

__all__ = ["all_rules"]
