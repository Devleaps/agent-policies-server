from devleaps.policies.server.common.models import ToolUseEvent, PolicyAction
from src.core import command, matches_regex
from src.utils import PolicyHelper


yarn_test_rule = (
    command("yarn")
    .subcommand("test")
    .allow()
)


yarn_start_rule = (
    command("yarn")
    .subcommand("start")
    .allow()
)


yarn_build_rule = (
    command("yarn")
    .subcommand("build")
    .allow()
)


yarn_remove_rule = (
    command("yarn")
    .subcommand("remove")
    .allow()
)


yarn_why_rule = (
    command("yarn")
    .subcommand("why")
    .with_argument(matches_regex(r'^[\w\-@/]+$'))
    .allow()
)


all_rules = [
    yarn_test_rule,
    yarn_start_rule,
    yarn_build_rule,
    yarn_remove_rule,
    yarn_why_rule,
]
