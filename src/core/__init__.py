"""Core components for AST-based command parsing and fluent rule building.

This module provides the foundation for the new bashlex-based policy system:
- BashCommandParser: Parse bash commands into structured AST
- Fluent API: Build rules declaratively without regex
- Matchers: Compositional validation (has_flag, require_one, etc.)
- Predicates: Reusable value validators (safe_path, localhost_url, etc.)
"""

from src.core.command_parser import BashCommandParser, ParsedCommand, ParseError
from src.core.bash_evaluator import evaluate_bash_rules
from src.core.rule_builder import command
from src.core.matchers import (
    matches_any,
    has_flag,
    has_option,
    has_argument,
    has_keyword,
    require_one,
    require_all,
    is_not,
    matches_subcommand,
)
from src.core.predicates import (
    safe_path,
    localhost_url,
    max_value,
    is_one_of,
    matches_regex,
    always_valid,
)

__all__ = [
    "BashCommandParser",
    "ParsedCommand",
    "ParseError",
    "evaluate_bash_rules",
    "command",
    "matches_any",
    "has_flag",
    "has_option",
    "has_argument",
    "has_keyword",
    "require_one",
    "require_all",
    "is_not",
    "matches_subcommand",
    "safe_path",
    "localhost_url",
    "max_value",
    "is_one_of",
    "matches_regex",
    "always_valid",
]
