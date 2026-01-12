"""Python-uv bundle - UV package manager policies merged with universal."""

from devleaps.policies.server.common.models import ToolUseEvent
from src.core import evaluate_bash_rules
from src.bundles.python_uv import policy
from src.bundles.python_uv.guidance import uv_pyproject_guidance_rule
from src.bundles.universal import all_bash_rules as universal_bash_rules

all_bash_rules = [
    *universal_bash_rules,
    *policy.all_rules,
]
all_post_file_edit_rules = [uv_pyproject_guidance_rule]


def bash_rules_bundle_python_uv(event: ToolUseEvent):
    """Evaluate all python-uv bash rules (including universal) against the event."""
    yield from evaluate_bash_rules(event, all_bash_rules)


__all__ = [
    "bash_rules_bundle_python_uv",
    "all_bash_rules",
    "all_post_file_edit_rules",
]
