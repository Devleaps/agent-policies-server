"""Bash command evaluation utilities."""

import re
from typing import List, Callable
from devleaps.policies.server.common.models import ToolUseEvent
from src.core.command_parser import BashCommandParser, ParsedCommand, ParseError
from src.utils import PolicyHelper


def walk_and_evaluate(event: ToolUseEvent, cmd: ParsedCommand, rules: List[Callable]):
    """Recursively walk command tree and evaluate all rules.

    Yields decisions from rules, or ASK if no rules matched.
    """
    decisions = []
    for rule in rules:
        for result in rule(event, cmd):
            decisions.append(result)

    if decisions:
        for decision in decisions:
            yield decision
    else:
        yield PolicyHelper.ask()

    for piped in cmd.pipes:
        yield from walk_and_evaluate(event, piped, rules)

    for chained in cmd.chained:
        yield from walk_and_evaluate(event, chained, rules)


def evaluate_bash_rules(event: ToolUseEvent, rules: List[Callable]):
    """Parse bash command and evaluate rules against each command in chain.

    Args:
        event: The ToolUseEvent to evaluate
        rules: List of rule functions to evaluate

    Yields:
        PolicyDecision or PolicyGuidance from rules, or ASK if no rules matched
    """
    if not event.tool_is_bash:
        return

    # Check for quoted heredoc delimiters before parsing (bashlex can't parse them)
    if re.search(r'<<\s*["\'][^"\']+["\']', event.command):
        yield PolicyHelper.deny(
            "Quoted heredoc delimiters (<< 'EOF' or << \"EOF\") are not allowed.\n"
            "Use unquoted delimiters instead (e.g., << EOF)."
        )
        return

    try:
        parsed = BashCommandParser.parse(event.command)
    except ParseError:
        return

    yield from walk_and_evaluate(event, parsed, rules)


__all__ = ["evaluate_bash_rules"]
