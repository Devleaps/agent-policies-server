"""Policy bundle functions for different project types."""

import re
from typing import Generator
from devleaps.policies.server.common.models import ToolUseEvent, PolicyDecision
from src.core.rego_integration import RegoEvaluator
from src.core.command_parser import BashCommandParser, ParseError
from src.utils import PolicyHelper

# Single shared evaluator - loads all policies once at module import
rego_evaluator = RegoEvaluator(policy_dir="policies")
# Import guidance rules from their current locations
# These remain in bundles/ subdirectories as they contain actual implementations
from src.bundles.universal.guidance.comment_ratio import comment_ratio_guidance_rule
from src.bundles.universal.guidance.comment_overlap import comment_overlap_guidance_rule
from src.bundles.universal.guidance.commented_code import commented_code_guidance_rule
from src.bundles.universal.guidance.legacy_code import legacy_code_guidance_rule
from src.bundles.universal.guidance.mid_code_import import mid_code_import_guidance_rule
from src.bundles.universal.guidance.readme_license import readme_license_guidance_rule
from src.bundles.python_uv.guidance import uv_pyproject_guidance_rule

all_guidance_rules = [
    comment_ratio_guidance_rule,
    comment_overlap_guidance_rule,
    commented_code_guidance_rule,
    legacy_code_guidance_rule,
    mid_code_import_guidance_rule,
    readme_license_guidance_rule,
]

all_python_uv_guidance_rules = [uv_pyproject_guidance_rule]


def _evaluate_bash_rules(event: ToolUseEvent, bundles: list[str]) -> Generator[PolicyDecision, None, None]:
    """Evaluate bash rules against the event using Rego policies.

    Args:
        event: The tool use event to evaluate
        bundles: List of Rego policy bundles to evaluate (e.g., ["universal"], ["universal", "python_uv"])
    """
    if not event.tool_is_bash:
        return

    # Check for quoted heredoc delimiters (not supported by bashlex)
    if re.search(r'<<\s*["\'][^"\']+["\']', event.command):
        yield PolicyHelper.deny(
            "Quoted heredoc delimiters (<< 'EOF' or << \"EOF\") are not allowed.\n"
            "Use unquoted delimiters instead (e.g., << EOF)."
        )
        return

    try:
        parsed = BashCommandParser.parse(event.command)
        decisions = rego_evaluator.evaluate(event, parsed, bundles=bundles)
        if decisions:
            yield from decisions
        else:
            yield PolicyHelper.ask()
    except ParseError:
        return


def bash_rules_bundle_universal(event: ToolUseEvent) -> Generator[PolicyDecision, None, None]:
    """Evaluate all universal bash rules against the event using Rego policies."""
    yield from _evaluate_bash_rules(event, bundles=["universal"])


def bash_rules_bundle_python_pip(event: ToolUseEvent) -> Generator[PolicyDecision, None, None]:
    """Evaluate all python-pip bash rules (including universal) against the event using Rego policies."""
    yield from _evaluate_bash_rules(event, bundles=["universal", "python_pip"])


def bash_rules_bundle_python_uv(event: ToolUseEvent) -> Generator[PolicyDecision, None, None]:
    """Evaluate all python-uv bash rules (including universal) against the event using Rego policies."""
    yield from _evaluate_bash_rules(event, bundles=["universal", "python_uv"])
