"""Python-pip bundle - pip package management and Python quality tools merged with universal."""

from devleaps.policies.server.common.models import ToolUseEvent
from src.core import evaluate_bash_rules
from src.bundles.python_pip import python_pip
from src.bundles.universal import all_bash_rules as universal_bash_rules

all_bash_rules = [
    *universal_bash_rules,
    *python_pip.all_rules,
]


def bash_rules_bundle_python_pip(event: ToolUseEvent):
    """Evaluate all python-pip bash rules (including universal) against the event."""
    yield from evaluate_bash_rules(event, all_bash_rules)


__all__ = [
    "bash_rules_bundle_python_pip",
    "all_bash_rules",
]
