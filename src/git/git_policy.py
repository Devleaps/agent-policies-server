"""Git add and commit policies with specific format requirements."""

import re
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper, path_appears_safe


def git_add_rule(input_data: ToolUseEvent):
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    if not re.match(r'^git\s+add\s+', command):
        return

    if re.match(r'^git\s+add\s+-A(?:\s|$)', command):
        yield PolicyHelper.allow()
        return

    yield PolicyHelper.allow()
    yield PolicyHelper.guidance(
        "When using `git add` with specific files, ensure you're not missing any files "
        "that would have been caught by `git add -A .`"
    )


def git_commit_rule(input_data: ToolUseEvent):
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    if not re.match(r'^git\s+commit(?:\s|$)', command):
        return

    # Allow if -m flag with quoted message OR --amend flag
    if re.search(r'\s-m\s+["\']', command) or re.search(r'--amend\b', command):
        yield PolicyHelper.allow()
        return

    # Deny anything else
    yield PolicyHelper.deny(
        "By policy, git commit requires the -m flag with a quoted message or --amend.\n"
        'Use `git commit -m "your message"` or `git commit --amend`.'
    )


def git_mv_rule(input_data: ToolUseEvent):
    """Allow git mv with workspace-relative paths only."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    if not re.match(r'^git\s+mv\s+', command):
        return

    # Strip "git mv" from the start
    args_part = re.sub(r'^git\s+mv\s+', '', command)

    # Split by whitespace and filter out flags (arguments starting with -)
    tokens = args_part.split()
    paths = [token for token in tokens if not token.startswith('-')]

    # Check all path arguments for safety
    for path in paths:
        is_safe, reason = path_appears_safe(path)
        if not is_safe:
            yield PolicyHelper.deny(f"git mv: {reason}")
            return

    # All paths are safe
    yield PolicyHelper.allow()


def git_push_force_rule(input_data: ToolUseEvent):
    """Block git push with --force or -f flag."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    if not re.match(r'^git\s+push\s+', command):
        return

    # Check for --force or -f flag
    if re.search(r'--force\b', command) or re.search(r'\s-f\b', command):
        yield PolicyHelper.deny(
            "Force push is not allowed.\n"
            "Force pushing can overwrite history and cause data loss for other collaborators."
        )


def git_rm_rule(input_data: ToolUseEvent):
    """Block git rm and suggest using trash instead."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    if not re.match(r'^git\s+rm\s+', command):
        return

    yield PolicyHelper.deny(
        "`git rm` is not allowed. Use `trash` instead.\n"
        "The macOS `trash` command safely moves files to Trash."
    )


all_rules = [git_add_rule, git_commit_rule, git_mv_rule, git_push_force_rule, git_rm_rule]
