"""Git add and commit policies with specific format requirements."""

import re
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def git_add_rule(input_data: ToolUseEvent):
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    if not re.match(r'^git\s+add\s+', command):
        return

    if re.match(r'^git\s+add\s+-A(?:\s|$)', command):
        yield PolicyHelper.allow()
        return

    yield PolicyHelper.deny(
        "By policy, git add requires the -A flag.\n"
        "Use `git add -A` to stage all changes."
    )


def git_commit_rule(input_data: ToolUseEvent):
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    if not re.match(r'^git\s+commit\s+', command):
        return

    if re.match(r'^git\s+commit\s+-m\s+["\']', command):
        yield PolicyHelper.allow()
        return

    yield PolicyHelper.deny(
        "By policy, git commit requires the -m flag with a quoted message.\n"
        'Use `git commit -m "your message"` format.'
    )


all_rules = [git_add_rule, git_commit_rule]
