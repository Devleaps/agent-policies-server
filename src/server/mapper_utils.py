"""
Shared mapper utilities for converting between editor-specific and generic models.

Provides common functionality used by both Claude Code and Cursor mappers.
"""

from typing import List, Optional, Tuple, Union

from .models import POLICY_PRECEDENCE, PolicyDecision, PolicyGuidance


def separate_results(
    results: List[Union[PolicyDecision, PolicyGuidance]],
) -> Tuple[List[PolicyDecision], List[PolicyGuidance]]:
    """
    Separate results into decisions and guidances, removing duplicates.

    Decisions are deduplicated by (action, reason) and guidances by content,
    preserving first-occurrence order.

    Args:
        results: Mixed list of PolicyDecision and PolicyGuidance objects

    Returns:
        Tuple of (decisions, guidances)
    """
    decisions: List[PolicyDecision] = []
    seen_decisions: set[Tuple[str, Optional[str]]] = set()
    guidances: List[PolicyGuidance] = []
    seen_guidances: set[str] = set()

    for r in results:
        if isinstance(r, PolicyDecision):
            key = (r.action, r.reason)
            if key not in seen_decisions:
                seen_decisions.add(key)
                decisions.append(r)
        elif isinstance(r, PolicyGuidance):
            if r.content not in seen_guidances:
                seen_guidances.add(r.content)
                guidances.append(r)

    return decisions, guidances


def find_highest_priority_decision(
    decisions: List[PolicyDecision],
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
