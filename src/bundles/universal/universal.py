import re
from typing import Tuple
from devleaps.policies.server.common.models import ToolUseEvent, PolicyAction
from src.core import command, matches_any, max_value, has_keyword, has_flag, BashCommandParser, ParseError, safe_path, is_not
from src.core.command_parser import ParsedCommand
from src.utils import PolicyHelper, path_appears_safe, path_in_command_appears_safe


def starts_with_absolute_path():
    """Custom matcher: check if command starts with absolute path."""
    def matcher(cmd: ParsedCommand) -> Tuple[bool, str]:
        if cmd.original.strip().startswith("/"):
            return True, ""
        return False, ""
    return matcher


def starts_with_venv_bin():
    """Custom matcher: check if command starts with .venv/bin/."""
    def matcher(cmd: ParsedCommand) -> Tuple[bool, str]:
        if cmd.original.strip().startswith(".venv/bin/"):
            return True, ""
        return False, ""
    return matcher


sudo_block_rule = (
    command("sudo")
    .deny(
        "By policy, sudo commands are not allowed for security reasons.\n"
        "Run commands without sudo privileges or configure appropriate permissions."
    )
)


kill_block_rule = (
    command("kill")
    .deny(
        "By policy, kill commands are not allowed.\n"
        "Use `pkill` instead for safer process termination (e.g., `pkill -f processname`)."
    )
)


xargs_block_rule = (
    command("xargs")
    .deny(
        "By policy, xargs is not allowed.\n"
        "xargs can execute arbitrary commands and bypass policy controls."
    )
)


timeout_block_rule = (
    command("timeout")
    .deny(
        "By policy, timeout commands are not allowed.\n"
        "Timeout can be used to wrap arbitrary commands and bypass policy controls."
    )
)


time_block_rule = (
    command("time")
    .deny(
        "By policy, time commands are not allowed.\n"
        "Time can be used to wrap arbitrary commands and bypass policy controls."
    )
)


awk_block_rule = (
    command("awk")
    .deny("By policy, awk commands are not allowed for security reasons.")
)


cat_rule = command("cat").with_arguments(safe_path).allow()


cp_rule = command("cp").with_arguments(safe_path).allow()


cut_rule = command("cut").with_arguments(safe_path).allow()


diff_rule = command("diff").with_arguments(safe_path).allow()


du_rule = command("du").with_arguments(safe_path).allow()


git_diff_rule = command("git").subcommand("diff").allow()


git_log_rule = command("git").subcommand("log").allow()


git_show_rule = command("git").subcommand("show").allow()


git_status_rule = command("git").subcommand("status").allow()


grep_rule = command("grep").allow()


lsof_rule = command("lsof").allow()


nslookup_rule = command("nslookup").allow()


pkill_rule = command("pkill").allow()


ps_rule = command("ps").allow()


pytest_rule = command("pytest").allow()


pwd_rule = command("pwd").allow()


head_rule = command("head").allow()


echo_rule = command("echo").allow()


ls_rule = command("ls").with_arguments(safe_path).allow()


mkdir_rule = command("mkdir").with_arguments(safe_path).allow()


sed_rule = command("sed").with_arguments(safe_path).allow()


sort_rule = command("sort").with_arguments(safe_path).allow()


source_venv_rule = command("source").when(has_keyword("venv/bin/activate")).allow()


tail_rule = command("tail").with_arguments(safe_path).allow()


tflint_rule = command("tflint").allow()


touch_rule = command("touch").with_arguments(safe_path).allow()


trash_rule = command("trash").with_arguments(safe_path).allow()


wc_rule = command("wc").with_arguments(safe_path).allow()


which_rule = command("which").allow()


true_rule = command("true").allow()


sleep_duration_rule = (
    command("sleep")
    .with_argument(max_value(60))
    .allow()
)


absolute_path_deny_rule = (
    command(matches_any)
    .when(starts_with_absolute_path())
    .deny(
        "Absolute path executables are not allowed.\n"
        "Use command names directly (e.g., `pytest`) or relative paths (e.g., `./scripts/run.sh`)."
    )
)

venv_bin_deny_rule = (
    command(matches_any)
    .when(starts_with_venv_bin())
    .deny(
        "Direct execution from `.venv/bin/` is not allowed.\n"
        "Use `uv run` to execute tools (e.g., `uv run pytest`)."
    )
)


rm_block_rule = (
    command("rm")
    .deny(
        "The `rm` command is not allowed.\n"
        "Always use `trash` instead. The macOS `trash` command safely moves files to Trash."
    )
)


def sqlite3_read_only_rule(event: ToolUseEvent, parsed):
    if not event.tool_is_bash:
        return

    if parsed.executable != "sqlite3":
        return

    command_upper = parsed.get_command_text().upper()

    write_operations = [
        'INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER',
        'CREATE', 'REPLACE', 'ATTACH', 'DETACH', 'PRAGMA'
    ]

    has_write_operation = any(
        re.search(rf'\b{op}\b', command_upper) for op in write_operations
    )

    if has_write_operation:
        yield PolicyHelper.deny(
            "By policy, sqlite3 write operations (INSERT, UPDATE, DELETE, DROP, ALTER, "
            "CREATE, REPLACE, ATTACH, DETACH, PRAGMA) are not allowed.\n"
            "Only SELECT queries are permitted for database read operations."
        )
        return

    has_select = re.search(r'\bSELECT\b', command_upper)

    if has_select:
        yield PolicyHelper.allow()
        return

    yield PolicyHelper.ask(
        "This sqlite3 command doesn't appear to contain a SELECT query. "
        "Only SELECT queries are allowed by policy. "
        "If you need to perform a read operation, please use SELECT."
    )


def safe_redirect_path(path: str):
    """Predicate: disallow redirects to /tmp/, /home/, and /etc/."""
    forbidden_prefixes = ['/tmp/', '/home/', '/etc/']
    for prefix in forbidden_prefixes:
        if path.startswith(prefix):
            return False, f"redirects to {prefix} are not allowed"
    return True, ""


unsafe_redirect_deny_rule = (
    command(matches_any)
    .forbid_redirects(safe_redirect_path)
    .deny(
        "Writing to `/tmp/`, `/home/`, or `/etc/` is not allowed.\n"
        "Use workspace-relative paths instead."
    )
)


def cd_has_safe_path(cmd: ParsedCommand):
    """Check if cd path is safe (skips dots/slashes only paths)."""
    if not cmd.arguments:
        return False, ""

    path = cmd.arguments[0]

    # Skip trivial paths (dots/slashes only) - handled by other rule
    if re.match(r'^[/.]*$', path) and path:
        return False, ""

    is_safe, reason = path_appears_safe(path)
    return is_safe, reason


cd_safe_allow_rule = (
    command("cd")
    .when(cd_has_safe_path)
    .allow()
)

cd_unsafe_deny_rule = (
    command("cd")
    .when(is_not(cd_has_safe_path))
    .deny(
        "By policy, cd with unsafe path.\n"
        "Use relative paths only (e.g., `cd subdir` or `cd project/src`).\n"
        "If you need to navigate upward, use paths like `cd ..` or `cd ../..`."
    )
)


def cd_dots_slashes_only(cmd: ParsedCommand):
    """Check if cd path contains only dots and slashes."""
    if not cmd.arguments:
        return False, ""

    path = cmd.arguments[0]
    if re.match(r'^[/.]+$', path):
        return True, ""
    return False, ""


cd_upward_navigation_rule = (
    command("cd")
    .when(cd_dots_slashes_only)
    .allow()
)


def no_flags_or_options(cmd: ParsedCommand):
    """Check that command has no flags or options."""
    if cmd.flags or cmd.options:
        return False, "command has flags or options"
    return True, ""


def mv_paths_safe(cmd: ParsedCommand):
    """Check if mv command paths are safe."""
    is_safe, reason = path_in_command_appears_safe(cmd.get_command_text(), "mv")
    if not is_safe:
        return False, reason
    return True, ""


mv_rule = (
    command("mv")
    .with_arguments(safe_path)
    .allow()
)


rmdir_rule = command("rmdir").with_arguments(safe_path).allow()


find_exec_rule = (
    command("find")
    .when(has_flag("-exec"))
    .deny("find commands with -exec are not allowed for security reasons")
)


find_safe_allow_rule = (
    command("find")
    .with_arguments(safe_path)
    .allow()
)

find_unsafe_deny_rule = (
    command("find")
    .deny(
        "By policy, find must use safe paths.\n"
        "Use relative paths only (e.g., `find . -name \"*.txt\"` or `find subdir -type f`).\n"
        "If you need to search upward, first `cd` to the target directory."
    )
)


all_rules = [
    absolute_path_deny_rule,
    awk_block_rule,
    cat_rule,
    cd_upward_navigation_rule,
    cd_safe_allow_rule,
    cd_unsafe_deny_rule,
    cp_rule,
    cut_rule,
    diff_rule,
    du_rule,
    echo_rule,
    find_exec_rule,
    find_safe_allow_rule,
    find_unsafe_deny_rule,
    git_diff_rule,
    git_log_rule,
    git_show_rule,
    git_status_rule,
    grep_rule,
    head_rule,
    kill_block_rule,
    lsof_rule,
    ls_rule,
    mkdir_rule,
    mv_rule,
    nslookup_rule,
    pkill_rule,
    ps_rule,
    pytest_rule,
    pwd_rule,
    rm_block_rule,
    rmdir_rule,
    sed_rule,
    sleep_duration_rule,
    sort_rule,
    source_venv_rule,
    sqlite3_read_only_rule,
    sudo_block_rule,
    tail_rule,
    tflint_rule,
    time_block_rule,
    timeout_block_rule,
    unsafe_redirect_deny_rule,
    touch_rule,
    trash_rule,
    true_rule,
    venv_bin_deny_rule,
    wc_rule,
    which_rule,
    xargs_block_rule,
]
