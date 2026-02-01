"""Evaluation engine for policy enforcement.

This module provides the foundation for the Rego-based policy system:
- BashCommandParser: Parse bash commands into structured AST
- RegoEvaluator: Evaluate Rego policies against commands
"""

from src.evaluation.parser import BashCommandParser, ParsedCommand, ParseError
from src.evaluation.rego import RegoEvaluator
from src.evaluation.handlers import evaluate_bash_rules, evaluate_guidance

__all__ = [
    "BashCommandParser",
    "ParsedCommand",
    "ParseError",
    "RegoEvaluator",
    "evaluate_bash_rules",
    "evaluate_guidance",
]
