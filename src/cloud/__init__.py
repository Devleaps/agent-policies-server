"""Cloud provider policies (az, kubectl, terraform, terragrunt, tflint, gh)."""

from src.cloud.az_list import azure_cli_list_rule
from src.cloud.az_show import azure_cli_show_rule
from src.cloud.az_default_block import azure_cli_default_block_rule
from src.cloud.kubectl_allow import kubectl_read_only_rule
from src.cloud.terraform_policy import (
    terraform_fmt_rule,
    terraform_plan_rule,
    terraform_default_block_rule
)
from src.cloud.terragrunt_policy import (
    terragrunt_plan_rule,
    terragrunt_default_block_rule
)
from src.cloud.gh_api import gh_api_rule

all_rules = [
    azure_cli_list_rule,
    azure_cli_show_rule,
    azure_cli_default_block_rule,
    kubectl_read_only_rule,
    terraform_fmt_rule,
    terraform_plan_rule,
    terraform_default_block_rule,
    terragrunt_plan_rule,
    terragrunt_default_block_rule,
    gh_api_rule,
]
