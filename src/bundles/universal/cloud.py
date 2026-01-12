from typing import Tuple
from devleaps.policies.server.common.models import ToolUseEvent, PolicyAction
from src.core import command, has_option, safe_path, is_one_of, BashCommandParser, ParseError, has_keyword, is_not
from src.core.command_parser import ParsedCommand
from src.utils import PolicyHelper


def subcommand_or_last_arg(value: str):
    """Custom matcher: check if subcommand OR last argument equals value."""
    def matcher(cmd: ParsedCommand) -> Tuple[bool, str]:
        if cmd.subcommand == value:
            return True, ""
        if cmd.arguments and cmd.arguments[-1] == value:
            return True, ""
        return False, f"must have '{value}' as subcommand or last argument"
    return matcher


def subcommand_in_list(*allowed: str):
    """Custom matcher: check if subcommand is in allowed list."""
    def matcher(cmd: ParsedCommand) -> Tuple[bool, str]:
        if cmd.subcommand in allowed:
            return True, ""
        return False, f"subcommand must be one of: {', '.join(allowed)}"
    return matcher


def subcommand_with_first_arg(subcommand: str, first_arg: str):
    """Custom matcher: check if subcommand matches AND first argument matches."""
    def matcher(cmd: ParsedCommand) -> Tuple[bool, str]:
        if cmd.subcommand != subcommand:
            return False, f"subcommand must be '{subcommand}'"
        if not cmd.arguments or cmd.arguments[0] != first_arg:
            return False, f"first argument must be '{first_arg}'"
        return True, ""
    return matcher


docker_build_rule = (
    command("docker")
    .subcommand("build")
    .with_arguments(safe_path)
    .allow()
)


gh_api_rule = (
    command("gh")
    .subcommand("api")
    .with_option("--method", is_one_of("GET"))
    .allow()
)


terraform_fmt_rule = (
    command("terraform")
    .subcommand("fmt")
    .allow()
)


terraform_plan_rule = (
    command("terraform")
    .subcommand("plan")
    .allow()
)


terraform_default_deny_rule = (
    command("terraform")
    .when(is_not(has_keyword("fmt"), has_keyword("plan")))
    .deny(
        "Only `terraform fmt` and `terraform plan` are allowed.\n"
        "Dangerous operations like apply, destroy, or init are not permitted."
    )
)


terragrunt_plan_rule = (
    command("terragrunt")
    .subcommand("plan")
    .allow()
)


terragrunt_default_deny_rule = (
    command("terragrunt")
    .when(is_not(has_keyword("plan")))
    .deny(
        "Only `terragrunt plan` is allowed.\n"
        "Dangerous operations like apply, destroy, or run-all are not permitted."
    )
)


azure_cli_list_rule = (
    command("az")
    .when(subcommand_or_last_arg("list"))
    .allow()
)

azure_cli_show_rule = (
    command("az")
    .when(subcommand_or_last_arg("show"))
    .allow()
)


azure_cli_default_deny_rule = (
    command("az")
    .when(is_not(has_keyword("list"), has_keyword("show")))
    .deny(
        "Only Azure CLI read-only commands with 'list' or 'show' are allowed.\n"
        "Dangerous operations like create, delete, update, or set are not permitted."
    )
)


kubectl_read_only_subcommands_rule = (
    command("kubectl")
    .when(subcommand_in_list(
        "get", "list", "describe", "logs", "top", "version",
        "api-versions", "api-resources", "explain", "cluster-info"
    ))
    .allow()
)

kubectl_config_view_rule = (
    command("kubectl")
    .when(subcommand_with_first_arg("config", "view"))
    .allow()
)

kubectl_auth_can_i_rule = (
    command("kubectl")
    .when(subcommand_with_first_arg("auth", "can-i"))
    .allow()
)

k_read_only_subcommands_rule = (
    command("k")
    .when(subcommand_in_list(
        "get", "list", "describe", "logs", "top", "version",
        "api-versions", "api-resources", "explain", "cluster-info"
    ))
    .allow()
)

k_config_view_rule = (
    command("k")
    .when(subcommand_with_first_arg("config", "view"))
    .allow()
)

k_auth_can_i_rule = (
    command("k")
    .when(subcommand_with_first_arg("auth", "can-i"))
    .allow()
)

kubectl_default_deny_rule = (
    command("kubectl")
    .deny("Only read-only kubectl operations are allowed")
)

k_default_deny_rule = (
    command("k")
    .deny("Only read-only kubectl operations are allowed")
)


all_rules = [
    docker_build_rule,
    gh_api_rule,
    terraform_fmt_rule,
    terraform_plan_rule,
    terraform_default_deny_rule,
    terragrunt_plan_rule,
    terragrunt_default_deny_rule,
    azure_cli_list_rule,
    azure_cli_show_rule,
    azure_cli_default_deny_rule,
    kubectl_read_only_subcommands_rule,
    kubectl_config_view_rule,
    kubectl_auth_can_i_rule,
    k_read_only_subcommands_rule,
    k_config_view_rule,
    k_auth_can_i_rule,
    kubectl_default_deny_rule,
    k_default_deny_rule,
]
