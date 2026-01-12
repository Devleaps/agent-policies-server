import re
from devleaps.policies.server.common.models import ToolUseEvent, PolicyAction
from src.core import command, has_keyword, has_flag, matches_regex, is_one_of, has_option, is_not
from src.core.command_parser import ParsedCommand
from src.utils import PolicyHelper
from src.bundles.python_pip.predicates import pypi_package_age_predicate, is_python


black_format_rule = (
    command("black")
    .allow()
)


mypy_check_rule = (
    command("mypy")
    .allow()
)


ruff_check_rule = (
    command("ruff")
    .subcommand("check")
    .allow()
)


ruff_format_rule = (
    command("ruff")
    .subcommand("format")
    .allow()
)


pytest_rule = (
    command("pytest")
    .allow()
)


pip_audit_rule = (
    command("pip")
    .subcommand("audit")
    .allow()
)


pip_freeze_rule = (
    command("pip")
    .subcommand("freeze")
    .allow()
)


pip_show_rule = (
    command("pip")
    .subcommand("show")
    .allow()
)


pip_uninstall_rule = (
    command("pip")
    .subcommand("uninstall")
    .allow()
)


pip_install_requirements_rule = (
    command("pip")
    .subcommand("install")
    .when(has_keyword("-r"), has_keyword("requirements.txt"))
    .allow()
)


def has_packages_not_requirements(cmd: ParsedCommand):
    """Check if command has package arguments (not requirement files)."""
    if "-r" in cmd.options or "--requirement" in cmd.options:
        return False, ""

    for arg in cmd.arguments:
        if not arg.startswith('-'):
            return True, ""

    return False, ""


def validate_pip_packages(cmd: ParsedCommand):
    """Validate all pip install packages via PyPI age check."""
    for arg in cmd.arguments:
        if arg.startswith('-'):
            continue

        is_valid, reason = pypi_package_age_predicate(arg)
        if not is_valid:
            return False, reason

    return True, ""


pip_install_allow_rule = (
    command("pip")
    .subcommand("install")
    .when(has_packages_not_requirements)
    .when(validate_pip_packages)
    .allow()
)

pip_install_deny_rule = (
    command("pip")
    .subcommand("install")
    .when(has_packages_not_requirements)
    .when(is_not(validate_pip_packages))
    .deny(
        "Package validation failed. Only packages 1+ year old are auto-whitelisted.\n"
        "For newer packages, request manual approval."
    )
)


python3_venv_rule = (
    command(is_python)
    .with_option("-m", is_one_of("venv"))
    .deny(
        "By policy, `python -m venv` is not allowed.\n"
        "Use `uv sync` for virtual environment management."
    )
)


python_script_rule = (
    command(is_python)
    .require_one(has_option("-c"))
    .deny(
        "By policy, python -c commands are not allowed.\n"
        "For scripts, place them in a directory and run with python.\n"
        "To test new functionality: add test cases and run with `pytest`.\n"
        "Quick verification scripts are discouraged - use the existing test framework instead."
    )
)


python_module_pytest_deny_rule = (
    command("python")
    .when(has_flag("-m"), has_keyword("pytest"))
    .deny(
        "By policy, `python -m pytest` have been disallowed.\n"
        "Use `pytest` directly."
    )
)

python3_module_pytest_deny_rule = (
    command("python3")
    .when(has_flag("-m"), has_keyword("pytest"))
    .deny(
        "By policy, `python -m pytest` have been disallowed.\n"
        "Use `pytest` directly."
    )
)

python_test_file_deny_rule = (
    command("python")
    .with_argument(matches_regex(r'^test_.*\.py$'))
    .deny(
        "By policy, direct execution of test files is not allowed.\n"
        "Use `pytest` to run tests."
    )
)

python3_test_file_deny_rule = (
    command("python3")
    .with_argument(matches_regex(r'^test_.*\.py$'))
    .deny(
        "By policy, direct execution of test files is not allowed.\n"
        "Use `pytest` to run tests."
    )
)


all_rules = [
    pip_install_allow_rule,
    pip_install_deny_rule,
    pip_install_requirements_rule,
    pip_freeze_rule,
    pip_uninstall_rule,
    pip_show_rule,
    pip_audit_rule,
    python3_venv_rule,
    python_script_rule,
    python_module_pytest_deny_rule,
    python3_module_pytest_deny_rule,
    python_test_file_deny_rule,
    python3_test_file_deny_rule,
    black_format_rule,
    ruff_check_rule,
    ruff_format_rule,
    mypy_check_rule,
    pytest_rule,
]
