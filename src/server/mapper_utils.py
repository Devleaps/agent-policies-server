"""
Shared mapper utilities for converting between editor-specific and generic models.

Provides common functionality used by both Claude Code and Cursor mappers.
"""

from typing import List, Optional, Tuple, Union

from .models import POLICY_PRECEDENCE, PolicyDecision, PolicyGuidance


def separate_results(
    results: List[Union[PolicyDecision, PolicyGuidance]]
) -> Tuple[List[PolicyDecision], List[PolicyGuidance]]:
    """
    Separate results into decisions and guidances.

    Args:
        results: Mixed list of PolicyDecision and PolicyGuidance objects

    Returns:
        Tuple of (decisions, guidances)
    """
    decisions = [r for r in results if isinstance(r, PolicyDecision)]
    guidances = [r for r in results if isinstance(r, PolicyGuidance)]
    return decisions, guidances


def find_highest_priority_decision(
    decisions: List[PolicyDecision]
) -> Optional[PolicyDecision]:
    """
    Find the highest priority decision based on POLICY_PRECEDENCE.

    Precedence order: DENY > ASK > ALLOW

    Args:
        decisions: List of policy decisions

    Returns:
        The highest priority decision, or None if list is empty
    """
    for action in POLICY_PRECEDENCE:
        matching = [d for d in decisions if d.action == action]
        if matching:
            return matching[0]
    return None
