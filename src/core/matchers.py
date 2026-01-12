"""Compositional matchers for validating parsed commands.

Matchers are functions that check properties of ParsedCommand objects.
They can be combined using require_one, require_all, and forbid.
"""

from typing import Callable, Tuple, Optional, List
from src.core.command_parser import ParsedCommand
from src.core.predicates import PredicateFunc, always_valid


MatcherFunc = Callable[[ParsedCommand], Tuple[bool, str]]


def matches_any(cmd: ParsedCommand) -> Tuple[bool, str]:
    """Matcher that matches any command.

    Returns:
        (True, "") for any command

    Example:
        Use with command(matches_any) to match all executables
    """
    return True, ""


def has_flag(*flag_names: str) -> MatcherFunc:
    """Check if command has any of the specified flags.

    Args:
        *flag_names: Flag names to check (e.g., "--force", "-f")

    Returns:
        Matcher function

    Example:
        has_flag("--force", "-f")(cmd) -> (True, "") if --force or -f present

    Note:
        Checks both cmd.flags and cmd.options keys, since parser may
        incorrectly treat boolean flags as options when followed by arguments.
    """
    def matcher(cmd: ParsedCommand) -> Tuple[bool, str]:
        for flag in flag_names:
            if flag in cmd.flags or flag in cmd.options:
                return True, ""
        return False, f"missing one of: {', '.join(flag_names)}"

    return matcher


def has_option(name: str, predicate: Optional[PredicateFunc] = None) -> MatcherFunc:
    """Check if command has an option, optionally validating its value.

    Args:
        name: Option name (e.g., "-m", "--message")
        predicate: Optional predicate to validate option value

    Returns:
        Matcher function

    Example:
        has_option("-m")(cmd) -> (True, "") if -m is present
        has_option("--tag", matches_regex(r'^[a-z]+$'))(cmd) -> validates tag value
    """
    predicate = predicate or always_valid

    def matcher(cmd: ParsedCommand) -> Tuple[bool, str]:
        if name not in cmd.options:
            return False, f"missing option: {name}"

        value = cmd.options[name]
        is_valid, reason = predicate(value)
        if not is_valid:
            return False, f"option {name}: {reason}"

        return True, ""

    return matcher


def has_argument(predicate: PredicateFunc, index: Optional[int] = None) -> MatcherFunc:
    """Check if command has an argument that passes predicate.

    Args:
        predicate: Predicate to validate argument value
        index: Optional index (None means any argument)

    Returns:
        Matcher function

    Example:
        has_argument(safe_path, index=0)(cmd) -> validates first argument
        has_argument(safe_path)(cmd) -> validates all arguments
    """
    def matcher(cmd: ParsedCommand) -> Tuple[bool, str]:
        if index is not None:
            if index >= len(cmd.arguments):
                return False, f"missing argument at index {index}"

            value = cmd.arguments[index]
            is_valid, reason = predicate(value)
            if not is_valid:
                return False, f"argument {index}: {reason}"

            return True, ""
        else:
            for i, arg in enumerate(cmd.arguments):
                is_valid, reason = predicate(arg)
                if not is_valid:
                    return False, f"argument {i}: {reason}"

            return True, ""

    return matcher


def has_keyword(keyword: str, case_sensitive: bool = False) -> MatcherFunc:
    """Check if keyword appears anywhere in the command.

    Args:
        keyword: Keyword to search for
        case_sensitive: Whether to do case-sensitive matching

    Returns:
        Matcher function

    Example:
        has_keyword("SELECT")(cmd) -> checks if SELECT appears in command
    """
    search_keyword = keyword if case_sensitive else keyword.upper()

    def matcher(cmd: ParsedCommand) -> Tuple[bool, str]:
        search_text = cmd.original if case_sensitive else cmd.original.upper()

        if search_keyword in search_text:
            return True, ""

        return False, f"missing keyword: {keyword}"

    return matcher


def require_one(*matchers: MatcherFunc) -> MatcherFunc:
    """Require that at least one of the matchers passes (OR logic).

    Args:
        *matchers: Matcher functions to check

    Returns:
        Matcher function

    Example:
        require_one(has_option("-m"), has_flag("--amend"))(cmd)
        -> passes if either -m option or --amend flag is present
    """
    def matcher(cmd: ParsedCommand) -> Tuple[bool, str]:
        reasons = []
        for m in matchers:
            is_match, reason = m(cmd)
            if is_match:
                return True, ""
            reasons.append(reason)

        return False, " OR ".join(reasons)

    return matcher


def require_all(*matchers: MatcherFunc) -> MatcherFunc:
    """Require that all matchers pass (AND logic).

    Args:
        *matchers: Matcher functions to check

    Returns:
        Matcher function

    Example:
        require_all(has_flag("-v"), has_option("--output"))(cmd)
        -> passes only if both -v flag and --output option are present
    """
    def matcher(cmd: ParsedCommand) -> Tuple[bool, str]:
        for m in matchers:
            is_match, reason = m(cmd)
            if not is_match:
                return False, reason

        return True, ""

    return matcher


def is_not(*matchers: MatcherFunc) -> MatcherFunc:
    """Check that none of the matchers match (inverse matcher).

    Args:
        *matchers: Matcher functions to check

    Returns:
        Matcher function that passes when all matchers fail

    Example:
        is_not(has_keyword("DELETE"), has_keyword("DROP"))(cmd)
        -> passes only if neither DELETE nor DROP appear in command
    """
    def matcher(cmd: ParsedCommand) -> Tuple[bool, str]:
        for m in matchers:
            is_match, reason = m(cmd)
            if is_match:
                return False, f"forbidden condition matched"

        return True, ""

    return matcher


def matches_subcommand(subcommand: str) -> MatcherFunc:
    """Check if command has a specific subcommand.

    Args:
        subcommand: Subcommand to match

    Returns:
        Matcher function
    """
    def matcher(cmd: ParsedCommand) -> Tuple[bool, str]:
        if cmd.subcommand == subcommand:
            return True, ""

        return False, f"subcommand does not match: expected {subcommand}, got {cmd.subcommand}"

    return matcher
