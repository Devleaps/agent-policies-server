"""Policy bundle functions for different project types."""

import re
import logging
from typing import Generator, Callable, Dict, Union
from src.server.models import (
    ToolUseEvent,
    PostFileEditEvent,
    PolicyDecision,
    PolicyGuidance,
)
from src.evaluation.rego import RegoEvaluator
from src.evaluation.parser import BashCommandParser, ParseError

from src.guidance.python_comments import (
    comment_ratio_guidance_rule,
    comment_overlap_guidance_rule,
    commented_code_guidance_rule,
    legacy_code_guidance_rule,
)
from src.guidance.python_imports import mid_code_import_guidance_rule
from src.guidance.documentation import license_guidance_rule
from src.guidance.package_management import uv_pyproject_guidance_rule

logger = logging.getLogger(__name__)

rego_evaluator = RegoEvaluator(policy_dir="policies")

# Guidance implementation registry - maps check names (from Rego) to Python implementations
GuidanceImplementation = Callable[
    [PostFileEditEvent], Generator[PolicyGuidance, None, None]
]

GUIDANCE_REGISTRY: Dict[str, GuidanceImplementation] = {
    "comment_ratio": comment_ratio_guidance_rule,
    "comment_overlap": comment_overlap_guidance_rule,
    "commented_code": commented_code_guidance_rule,
    "legacy_code": legacy_code_guidance_rule,
    "mid_code_import": mid_code_import_guidance_rule,
    "license": license_guidance_rule,
    "uv_pyproject": uv_pyproject_guidance_rule,
}


def evaluate_bash_rules(
    event: ToolUseEvent,
) -> Generator[Union[PolicyDecision, PolicyGuidance], None, None]:
    """Evaluate bash rules against the event using Rego policies.

    Bundles to evaluate are read from event.enabled_bundles (defaults to ['universal']).
    Yields both PolicyDecision and PolicyGuidance objects.
    """
    if not event.tool_is_bash:
        return

    # Check for quoted heredoc delimiters (not supported by bashlex)
    if event.command and re.search(r'<<\s*["\'][^"\']+["\']', event.command):
        yield PolicyDecision.deny(
            "Quoted heredoc delimiters (<< 'EOF' or << \"EOF\") are not allowed.\n"
            "Use unquoted delimiters instead (e.g., << EOF)."
        )
        return

    try:
        command = event.command or ""
        parsed = BashCommandParser.parse(command)
        decisions = rego_evaluator.evaluate(
            event, parsed, bundles=event.enabled_bundles
        )
        if decisions:
            yield from decisions
        else:
            yield PolicyDecision.ask()

        # Also yield Rego guidances for bash commands
        guidances = rego_evaluator.evaluate_guidances(
            event, parsed, bundles=event.enabled_bundles
        )
        yield from guidances
    except ParseError:
        return


def evaluate_guidance(
    event: PostFileEditEvent,
) -> Generator[Union[PolicyDecision, PolicyGuidance], None, None]:
    """Evaluate guidance checks and file-edit decisions using Rego rules.

    Bundles to evaluate are read from event.enabled_bundles (defaults to ['universal']).

    Yields both PolicyDecision objects (for flag-setting rules) and PolicyGuidance objects
    (for guidance checks). The executor processes flags from PolicyDecision objects.
    """
    # Evaluate file-edit decisions (e.g., flag-setting rules like invalidating ran_tests)
    file_edit_decisions = rego_evaluator.evaluate_file_edit_decisions(
        event, bundles=event.enabled_bundles
    )
    if file_edit_decisions:
        yield from file_edit_decisions

    # Evaluate Rego guidances for file edits (may trigger on file_path alone, no structured_patch needed)
    rego_guidances = rego_evaluator.evaluate_file_edit_guidances(
        event, bundles=event.enabled_bundles
    )
    yield from rego_guidances

    if not event.structured_patch:
        return

    activated_checks = rego_evaluator.evaluate_guidance_activations(
        event, bundles=event.enabled_bundles
    )

    logger.debug(f"Activated guidance checks: {activated_checks}")

    for check_name in activated_checks:
        try:
            guidance_impl = GUIDANCE_REGISTRY[check_name]
            yield from guidance_impl(event)
        except KeyError:
            logger.error(
                f"Unknown guidance check '{check_name}' - not registered in GUIDANCE_REGISTRY"
            )
        except Exception as e:
            logger.error(f"Error running guidance check '{check_name}': {e}")
