from typing import Tuple
from devleaps.policies.server.common.models import ToolUseEvent, PolicyAction
from src.core import command, has_keyword, matches_regex, has_option, has_argument
from src.core.command_parser import ParsedCommand
from src.core.predicates import is_one_of
from src.utils import PolicyHelper
from src.bundles.python_pip.predicates import pypi_package_age_predicate, is_python


uv_pip_direct_deny_rule = (
    command("pip")
    .deny(
        "Direct `pip` usage is not allowed.\n"
        "To add dependencies: use `uv add package-name` (has integrated whitelist).\n"
        "To sync existing dependencies: use `uv sync`.\n"
        "Example: `uv add requests`"
    )
)


uv_pip_run_deny_rule = (
    command("uv")
    .subcommand("run")
    .when(has_argument(is_one_of("pip"), index=0))
    .deny(
        "Arbitrary `pip` installation not allowed via `uv run`.\n"
        "To add dependencies: use `uv add package-name` (has integrated whitelist).\n"
        "To sync existing dependencies: use `uv sync`.\n"
        "Example: `uv add requests`"
    )
)


uv_pip_install_deny_rule = (
    command("uv")
    .subcommand("pip")
    .when(has_argument(is_one_of("install"), index=0))
    .deny(
        "`uv pip install` is not allowed. Use `uv add` instead for better dependency management.\n"
        "Example: `uv add package-name`"
    )
)


uv_venv_deny_rule = (
    command("python")
    .when(has_keyword("-m"), has_keyword("venv"))
    .deny(
        "Direct venv creation not allowed.\n"
        "UV manages environments automatically - use 'uv sync' instead."
    )
)


uv_sync_allow_rule = (
    command("uv")
    .subcommand("sync")
    .allow()
)


black_direct_deny_rule = (
    command("black")
    .deny("Black must be run via uv.\nUse: uv run black .")
)

ruff_direct_deny_rule = (
    command("ruff")
    .deny("Ruff must be run via uv.\nUse: uv run ruff check . OR uv run ruff format .")
)

mypy_direct_deny_rule = (
    command("mypy")
    .deny("Mypy must be run via uv.\nUse: uv run mypy .")
)

pytest_direct_deny_rule = (
    command("pytest")
    .deny("Pytest must be run via uv.\nUse: uv run pytest")
)


uv_run_black_allow_rule = (
    command("uv")
    .subcommand("run")
    .when(has_argument(is_one_of("black"), index=0))
    .allow()
)

uv_run_ruff_allow_rule = (
    command("uv")
    .subcommand("run")
    .when(has_argument(is_one_of("ruff"), index=0))
    .allow()
)

uv_run_mypy_allow_rule = (
    command("uv")
    .subcommand("run")
    .when(has_argument(is_one_of("mypy"), index=0))
    .allow()
)

uv_run_pytest_allow_rule = (
    command("uv")
    .subcommand("run")
    .when(has_argument(is_one_of("pytest"), index=0))
    .allow()
)


def uv_requirements_txt_deny_rule(event: ToolUseEvent, parsed):
    if event.tool_name not in ("Write", "Edit"):
        return

    parameters = event.parameters
    if isinstance(parameters, dict):
        file_path = parameters.get("file_path", "")
        if file_path.endswith("requirements.txt"):
            yield PolicyHelper.deny(
                "Don't use requirements.txt. Use pyproject.toml instead.\n"
                "Use 'uv add package-name' to add dependencies to pyproject.toml."
            )


uv_python_module_deny_rule = (
    command(is_python)
    .require_one(has_option("-m"))
    .deny(
        "Direct python execution not allowed. Use `uv run` instead.\n"
        "Example: `python -m pytest` → `uv run pytest`"
    )
)


uv_python_scripts_ask_rule = (
    command(is_python)
    .when(has_keyword("scripts/"))
    .ask()
)


uv_python_direct_deny_rule = (
    command(is_python)
    .deny(
        "Direct python execution not allowed. Use `uv run` instead.\n"
        "Example: `python script.py` → `uv run script.py`\n"
        "Or move scripts to `scripts/` folder for user review."
    )
)


uv_add_validate_rule = (
    command("uv")
    .subcommand("add")
    .with_argument(pypi_package_age_predicate)
    .allow()
)


all_rules = [
    uv_pip_direct_deny_rule,
    uv_pip_run_deny_rule,
    uv_pip_install_deny_rule,
    uv_venv_deny_rule,
    uv_sync_allow_rule,
    uv_run_black_allow_rule,
    uv_run_ruff_allow_rule,
    uv_run_mypy_allow_rule,
    uv_run_pytest_allow_rule,
    black_direct_deny_rule,
    ruff_direct_deny_rule,
    mypy_direct_deny_rule,
    pytest_direct_deny_rule,
    uv_requirements_txt_deny_rule,
    uv_python_module_deny_rule,
    uv_python_scripts_ask_rule,
    uv_python_direct_deny_rule,
    uv_add_validate_rule,
]
