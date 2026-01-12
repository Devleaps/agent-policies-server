"""Reusable validation predicates for command arguments and options.

Predicates are functions that validate values and return (is_valid, reason) tuples.
They can be used in the fluent API for argument and option validation.
"""

import re
from typing import Callable, Tuple
from src.utils import path_appears_safe as _path_appears_safe, url_is_localhost as _url_is_localhost


PredicateFunc = Callable[[str], Tuple[bool, str]]


def safe_path(value: str) -> Tuple[bool, str]:
    """Validate that a path is safe (no absolute paths, no traversal, no /tmp).

    Returns:
        (True, "") if valid
        (False, reason) if invalid
    """
    return _path_appears_safe(value)


def localhost_url(value: str) -> Tuple[bool, str]:
    """Validate that a URL points to localhost.

    Returns:
        (True, "") if localhost
        (False, reason) if not localhost
    """
    if _url_is_localhost(value):
        return True, ""
    return False, f"URL must point to localhost, got: {value}"


def max_value(max_val: int) -> PredicateFunc:
    """Create a predicate that validates a number is <= max_val.

    Args:
        max_val: Maximum allowed value

    Returns:
        Predicate function

    Example:
        max_value(300)("250") -> (True, "")
        max_value(300)("500") -> (False, "value 500 exceeds maximum 300")
    """
    def validate(value: str) -> Tuple[bool, str]:
        try:
            num = int(value)
            if num <= max_val:
                return True, ""
            return False, f"value {num} exceeds maximum {max_val}"
        except ValueError:
            return False, f"expected number, got: {value}"

    return validate


def min_value(min_val: int) -> PredicateFunc:
    """Create a predicate that validates a number is >= min_val.

    Args:
        min_val: Minimum allowed value

    Returns:
        Predicate function
    """
    def validate(value: str) -> Tuple[bool, str]:
        try:
            num = int(value)
            if num >= min_val:
                return True, ""
            return False, f"value {num} is below minimum {min_val}"
        except ValueError:
            return False, f"expected number, got: {value}"

    return validate


def is_one_of(*allowed_values: str) -> PredicateFunc:
    """Create a predicate that validates a value is in the allowed list.

    Args:
        *allowed_values: Allowed values

    Returns:
        Predicate function

    Example:
        is_one_of("GET", "POST")("GET") -> (True, "")
        is_one_of("GET", "POST")("DELETE") -> (False, "value must be one of: GET, POST")
    """
    allowed_set = set(allowed_values)

    def validate(value: str) -> Tuple[bool, str]:
        if value in allowed_set:
            return True, ""
        return False, f"value must be one of: {', '.join(sorted(allowed_set))}"

    return validate


def matches_regex(pattern: str, description: str = None) -> PredicateFunc:
    """Create a predicate that validates a value matches a regex pattern.

    Args:
        pattern: Regular expression pattern
        description: Optional description for error messages

    Returns:
        Predicate function

    Example:
        matches_regex(r'^[a-z0-9-]+$')("my-app") -> (True, "")
        matches_regex(r'^[a-z0-9-]+$')("My App") -> (False, "value does not match pattern")
    """
    compiled = re.compile(pattern)
    desc = description or f"pattern {pattern}"

    def validate(value: str) -> Tuple[bool, str]:
        if compiled.match(value):
            return True, ""
        return False, f"value does not match {desc}"

    return validate


def matches_email(value: str) -> Tuple[bool, str]:
    """Validate that a value looks like an email address.

    Returns:
        (True, "") if valid email format
        (False, reason) if invalid
    """
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(email_pattern, value):
        return True, ""
    return False, "value must be a valid email address"


def not_empty(value: str) -> Tuple[bool, str]:
    """Validate that a value is not empty.

    Returns:
        (True, "") if not empty
        (False, reason) if empty
    """
    if value and value.strip():
        return True, ""
    return False, "value cannot be empty"


def always_valid(value: str) -> Tuple[bool, str]:
    """Predicate that always returns valid (used for presence checking only).

    Returns:
        (True, "")
    """
    return True, ""
