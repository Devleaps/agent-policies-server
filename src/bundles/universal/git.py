from devleaps.policies.server.common.models import PolicyAction
from src.core import command, has_option, has_flag, require_one, safe_path


git_add_all_rule = (
    command("git")
    .subcommand("add")
    .when(has_flag("-A"))
    .allow()
)


git_add_paths_rule = (
    command("git")
    .subcommand("add")
    .with_arguments(safe_path)
    .allow()
)


git_commit_rule = (
    command("git")
    .subcommand("commit")
    .require_one(
        has_option("-m"),
        has_option("--message"),
        has_flag("--amend")
    )
    .allow()
)


git_mv_rule = (
    command("git")
    .subcommand("mv")
    .with_arguments(safe_path)
    .allow()
)


git_push_force_rule = (
    command("git")
    .subcommand("push")
    .when(has_flag("--force", "-f"))
    .deny(
        "Force push is not allowed.\n"
        "Force pushing can overwrite history and cause data loss for other collaborators."
    )
)


git_rm_rule = (
    command("git")
    .subcommand("rm")
    .deny(
        "`git rm` is not allowed. Use `trash` instead.\n"
        "The macOS `trash` command safely moves files to Trash."
    )
)


git_branch_delete_force_rule = (
    command("git")
    .subcommand("branch")
    .when(has_flag("-D"))
    .deny(
        "`git branch -D` is not allowed.\n"
        "Force-deleting branches can result in data loss."
    )
)


git_checkout_rule = (
    command("git")
    .subcommand("checkout")
    .allow()
)


git_fetch_rule = (
    command("git")
    .subcommand("fetch")
    .allow()
)


git_pull_rule = (
    command("git")
    .subcommand("pull")
    .allow()
)


all_rules = [
    git_add_all_rule,
    git_add_paths_rule,
    git_commit_rule,
    git_mv_rule,
    git_push_force_rule,
    git_rm_rule,
    git_branch_delete_force_rule,
    git_checkout_rule,
    git_fetch_rule,
    git_pull_rule,
]
