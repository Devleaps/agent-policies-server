"""GitHub CLI gh api command policy."""

import re
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def gh_api_rule(input_data: ToolUseEvent):
    """Block gh api unless --method GET is explicitly specified."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    if not re.match(r'^gh\s+api\s+', command):
        return

    if re.search(r'--method\s+GET\b', command):
        yield PolicyHelper.allow()
        return

    yield PolicyHelper.deny(
        "`gh api` requires explicit `--method GET` to prevent accidental mutations.\n"
        "Use `gh api --method GET <endpoint>` for read-only operations."
    )


all_rules = [gh_api_rule]
