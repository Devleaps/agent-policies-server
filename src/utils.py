"""
Utilities for policy enforcement.

This module provides helper functions and classes for creating policy decisions
and performing common security checks.
"""
from urllib.parse import urlparse
from devleaps.policies.server.common.models import PolicyDecision, PolicyGuidance, PolicyAction


class PolicyHelper:
    """Helper class for creating policy decisions and guidance."""

    @staticmethod
    def deny(reason: str) -> PolicyDecision:
        """Create a DENY decision with the given reason."""
        return PolicyDecision(
            action=PolicyAction.DENY,
            reason=reason
        )

    @staticmethod
    def allow(reason: str = None) -> PolicyDecision:
        """Create an ALLOW decision with an optional reason."""
        return PolicyDecision(
            action=PolicyAction.ALLOW,
            reason=reason
        )

    @staticmethod
    def ask(reason: str = None) -> PolicyDecision:
        """Create an ASK decision (prompt user) with an optional reason."""
        return PolicyDecision(
            action=PolicyAction.ASK,
            reason=reason
        )

    @staticmethod
    def halt(reason: str = None) -> PolicyDecision:
        """Create a HALT decision (stop entire process) with an optional reason."""
        return PolicyDecision(
            action=PolicyAction.HALT,
            reason=reason
        )

    @staticmethod
    def guidance(content: str) -> PolicyGuidance:
        """Create guidance without making a decision."""
        return PolicyGuidance(content=content)


def path_appears_safe(path: str) -> tuple[bool, str]:
    """
    Check if a path appears safe from common mistakes in working with paths.

    Args:
        path: A path string to validate

    Returns:
        tuple[bool, str]: (is_safe, reason_if_unsafe)
    """
    # Check if path begins with /
    if path.startswith('/'):
        return False, "absolute paths are not allowed"

    # Check if path equals ..
    if path == '..':
        return False, "upward directory traversal (..) is not allowed"

    # Check if path contains ../
    if '../' in path:
        return False, "upward directory traversal (../) is not allowed"

    # Check if path contains /..
    if '/..' in path:
        return False, "upward directory traversal (/..) is not allowed"

    return True, ""


def path_in_command_appears_safe(command: str, command_name: str) -> tuple[bool, str]:
    """
    Extract paths from a command and check if they appear safe.

    Args:
        command: Full command string (e.g., "rm file.txt" or "find . -name '*.py'")
        command_name: The command name to strip (e.g., "rm", "find", "mv")

    Returns:
        tuple[bool, str]: (is_safe, reason_if_unsafe)
    """
    import re

    # Extract paths from command (everything after the command name)
    paths_part = re.sub(rf'^{re.escape(command_name)}\s+', '', command)

    # Check path safety
    return path_appears_safe(paths_part)


def url_is_localhost(url: str) -> bool:
    """
    Check if a URL points to localhost.

    Handles various localhost formats:
    - localhost (any port)
    - 127.x.x.x (any IP in 127.0.0.0/8 range)
    - ::1 (IPv6 localhost)

    Args:
        url: URL string or hostname to check

    Returns:
        bool: True if URL points to localhost, False otherwise
    """
    # Handle URLs without a scheme
    if not url.startswith(('http://', 'https://', '//')):
        # Try parsing as-is first (might be just a hostname)
        test_url = f'http://{url}'
    else:
        test_url = url

    try:
        parsed = urlparse(test_url)
        hostname = parsed.hostname or parsed.netloc.split(':')[0]

        # Check for localhost
        if hostname == 'localhost':
            return True

        # Check for IPv6 localhost
        if hostname == '::1':
            return True

        # Check for 127.x.x.x range
        if hostname.startswith('127.'):
            return True

        return False
    except Exception:
        # If parsing fails, fall back to simple string matching
        return any(pattern in url for pattern in ['localhost', '127.', '::1'])
