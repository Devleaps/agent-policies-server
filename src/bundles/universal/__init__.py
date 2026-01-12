"""Universal bundle - policies that apply to all projects."""

from devleaps.policies.server.common.models import ToolUseEvent
from src.core import evaluate_bash_rules
from src.bundles.universal import cloud, git, js, network, universal
from src.bundles.universal.guidance import all_guidance_rules


all_bash_rules = [
    *cloud.all_rules,
    *git.all_rules,
    *js.all_rules,
    *network.all_rules,
    *universal.all_rules,
]


def bash_rules_bundle_universal(event: ToolUseEvent):
    """Evaluate all universal bash rules against the event."""
    yield from evaluate_bash_rules(event, all_bash_rules)


__all__ = [
    "bash_rules_bundle_universal",
    "all_bash_rules",
    "all_guidance_rules",
]
