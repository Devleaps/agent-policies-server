"""Fluent API for building policy rules using method chaining.

Provides a declarative way to build policy rules without writing regex patterns.
"""

from typing import List, Optional, Callable, Union
from devleaps.policies.server.common.models import ToolUseEvent, PolicyAction
from src.core.command_parser import BashCommandParser, ParsedCommand, ParseError
from src.core.matchers import MatcherFunc, has_argument, require_one, require_all, is_not
from src.core.predicates import PredicateFunc
from src.utils import PolicyHelper


class RuleBuilder:
    """Fluent API for building policy rules.

    Examples:
        # String executable with deny
        rule = (
            command("git")
            .subcommand("commit")
            .require_one(has_option("-m"), has_flag("--amend"))
            .deny("Git commit requires `-m \"message\"` or `--amend`")
        )

        # Matcher function (e.g., is_python matches python, python3, python3.9)
        rule = (
            command(is_python)
            .require_one(has_option("-c"))
            .deny("python -c not allowed")
        )

        # Allow with validation
        rule = (
            command("sleep")
            .with_argument(max_value(60))
            .allow()
        )
    """

    def __init__(self, executable: Union[str, MatcherFunc]):
        """Initialize rule builder for an executable.

        Args:
            executable: Command executable name or a matcher function
        """
        if callable(executable):
            self._executable = None
            self._executable_matcher: Optional[MatcherFunc] = executable
        else:
            self._executable = executable
            self._executable_matcher: Optional[MatcherFunc] = None

        self._subcommand: Optional[str] = None
        self._matchers: List[MatcherFunc] = []
        self._argument_predicates: List[PredicateFunc] = []
        self._all_arguments_predicate: Optional[PredicateFunc] = None
        self._required_options: dict = {}
        self._optional_option_validators: dict = {}
        self._when_matchers: List[MatcherFunc] = []
        self._deny_reason_text: Optional[str] = None

    def subcommand(self, name: str) -> 'RuleBuilder':
        """Specify a required subcommand.

        Args:
            name: Subcommand name (e.g., "add" for "git add")

        Returns:
            Self for chaining
        """
        self._subcommand = name
        return self

    def with_argument(self, predicate: PredicateFunc) -> 'RuleBuilder':
        """Validate the next sequential argument.

        Args:
            predicate: Predicate to validate argument value

        Returns:
            Self for chaining

        Example:
            .with_argument(safe_path)  # arg 0
            .with_argument(safe_path)  # arg 1
        """
        self._argument_predicates.append(predicate)
        return self

    def with_arguments(self, predicate: PredicateFunc) -> 'RuleBuilder':
        """Validate all arguments with the same predicate.

        Args:
            predicate: Predicate to validate all argument values

        Returns:
            Self for chaining

        Example:
            .with_arguments(safe_path)  # ALL args must be safe paths
        """
        self._all_arguments_predicate = predicate
        return self

    def with_option(self, name: str, predicate: Optional[PredicateFunc] = None) -> 'RuleBuilder':
        """Require an option to be present, optionally validating its value.

        Args:
            name: Option name (e.g., "-m", "--message")
            predicate: Optional predicate to validate option value

        Returns:
            Self for chaining

        Example:
            .with_option("--tag", matches_regex(r'^[a-z0-9-]+$'))
        """
        self._required_options[name] = predicate
        return self

    def validate_option(self, name: str, predicate: PredicateFunc) -> 'RuleBuilder':
        """Validate an option if present (optional but validated).

        Args:
            name: Option name
            predicate: Predicate to validate option value

        Returns:
            Self for chaining

        Example:
            .validate_option("--author", matches_email)
        """
        self._optional_option_validators[name] = predicate
        return self

    def require_one(self, *matchers: MatcherFunc) -> 'RuleBuilder':
        """Require at least one matcher to pass (OR logic).

        Args:
            *matchers: Matcher functions

        Returns:
            Self for chaining

        Example:
            .require_one(has_option("-m"), has_flag("--amend"))
        """
        self._matchers.append(require_one(*matchers))
        return self

    def require_all(self, *matchers: MatcherFunc) -> 'RuleBuilder':
        """Require all matchers to pass (AND logic).

        Args:
            *matchers: Matcher functions

        Returns:
            Self for chaining
        """
        self._matchers.append(require_all(*matchers))
        return self

    def when(self, *matchers: MatcherFunc) -> 'RuleBuilder':
        """Set conditional matchers (rule only applies when these match).

        Args:
            *matchers: Matcher functions for conditional matching

        Returns:
            Self for chaining

        Example:
            .when(has_flag("--force"))
            .decide(match=DENY, no_match=NONE)
        """
        self._when_matchers.extend(matchers)
        return self

    def forbid_redirects(self, predicate: PredicateFunc) -> 'RuleBuilder':
        """Deny when redirects fail the predicate validation.

        This adds a conditional matcher - the rule only applies when a redirect fails validation.

        Args:
            predicate: Predicate to validate redirect paths (returns True if valid)

        Returns:
            Self for chaining

        Example:
            command(matches_any)
            .forbid_redirects(lambda path: (not path.startswith("/"), "absolute paths not allowed"))
            .deny("Absolute path redirects not allowed")
        """
        def redirect_matcher(cmd: ParsedCommand) -> tuple[bool, str]:
            for op, path in cmd.redirects:
                is_valid, reason = predicate(path)
                if not is_valid:
                    return True, f"redirect {op} {path}: {reason}"
            return False, ""

        self._when_matchers.append(redirect_matcher)
        return self

    def allow(self) -> Callable:
        """Allow when rule matches and validation passes.

        Returns:
            Rule function

        Example:
            .with_argument(max_value(60))
            .allow()
        """
        return self._build_rule(PolicyAction.ALLOW)

    def deny(self, reason: str) -> Callable:
        """Deny when rule matches.

        Args:
            reason: Reason for denying the command

        Returns:
            Rule function

        Example:
            .deny("sudo not allowed for security reasons")
        """
        self._deny_reason_text = reason
        return self._build_rule(PolicyAction.DENY)

    def ask(self, reason: Optional[str] = None) -> Callable:
        """Ask user when rule matches.

        Args:
            reason: Optional context/reason for asking

        Returns:
            Rule function

        Example:
            .when(has_keyword("scripts/"))
            .ask()
        """
        self._deny_reason_text = reason
        return self._build_rule(PolicyAction.ASK)

    def _build_rule(self, action: str) -> Callable:
        """Build the final rule function."""
        def rule_function(event: ToolUseEvent, parsed: ParsedCommand):
            if not event.tool_is_bash:
                return

            if not parsed:
                return

            # Check executable matcher or string match
            if self._executable_matcher:
                is_match, _ = self._executable_matcher(parsed)
                if not is_match:
                    return
            elif self._executable and parsed.executable != self._executable:
                return

            # Check subcommand match (early return if doesn't match)
            if self._subcommand and parsed.subcommand != self._subcommand:
                return

            if self._when_matchers:
                all_when_match = all(m(parsed)[0] for m in self._when_matchers)
                if not all_when_match:
                    return

            validation_result, reason = self._validate_command(parsed)

            if validation_result:
                yield self._make_decision(action, parsed)
            else:
                yield PolicyHelper.deny(self._deny_reason_text or reason)

        return rule_function

    def _matches_executable(self, command: str) -> bool:
        """Quick check if command might match this rule's executable."""
        if self._executable_matcher or not self._executable:
            return True
        return command.strip().startswith(self._executable)

    def _validate_command(self, cmd: ParsedCommand) -> tuple[bool, str]:
        """Validate command against all matchers and predicates."""
        for matcher in self._matchers:
            is_match, reason = matcher(cmd)
            if not is_match:
                return False, reason

        for i, predicate in enumerate(self._argument_predicates):
            if i >= len(cmd.arguments):
                return False, f"missing argument at position {i}"

            is_valid, reason = predicate(cmd.arguments[i])
            if not is_valid:
                return False, f"argument {i}: {reason}"

        if self._all_arguments_predicate:
            for i, arg in enumerate(cmd.arguments):
                is_valid, reason = self._all_arguments_predicate(arg)
                if not is_valid:
                    return False, f"argument {i}: {reason}"

        for opt_name, predicate in self._required_options.items():
            if opt_name not in cmd.options:
                return False, f"missing required option: {opt_name}"

            if predicate:
                value = cmd.options[opt_name]
                is_valid, reason = predicate(value)
                if not is_valid:
                    return False, f"option {opt_name}: {reason}"

        for opt_name, predicate in self._optional_option_validators.items():
            if opt_name in cmd.options:
                value = cmd.options[opt_name]
                is_valid, reason = predicate(value)
                if not is_valid:
                    return False, f"option {opt_name}: {reason}"

        return True, ""

    def _make_decision(self, action: str, cmd: ParsedCommand):
        """Make a policy decision based on action type."""
        if action == PolicyAction.ALLOW:
            return PolicyHelper.allow()
        elif action == PolicyAction.DENY:
            return PolicyHelper.deny(self._deny_reason_text or "Command not allowed")
        elif action == PolicyAction.ASK:
            return PolicyHelper.ask(self._deny_reason_text)
        else:
            return None


def command(executable: Union[str, MatcherFunc]) -> RuleBuilder:
    """Start building a policy rule for an executable.

    Args:
        executable: Command executable name or a matcher function

    Returns:
        RuleBuilder for method chaining

    Examples:
        command("git").subcommand("add").allow()
        command(matches_any).when(has_flag("--force")).deny()
        command(is_python).deny()
    """
    return RuleBuilder(executable)
