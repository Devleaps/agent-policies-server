from src.az.list import azure_cli_list_rule
from src.az.show import azure_cli_show_rule
from src.az.default_block import azure_cli_default_block_rule

all_rules = [azure_cli_list_rule, azure_cli_show_rule, azure_cli_default_block_rule]