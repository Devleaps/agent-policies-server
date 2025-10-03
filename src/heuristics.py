"""
Common heuristics for policy enforcement.

These functions provide reusable checks for various security and safety patterns.
"""


def path_appears_safe(path_or_command: str) -> tuple[bool, str]:
    """
    Check if a path or command appears safe from common mistakes in working with paths.

    Returns:
        tuple[bool, str]: (is_safe, reason_if_unsafe)
    """
    # Split by spaces and check each part
    parts = path_or_command.split()
    for part in parts:
        # Skip flags
        if part.startswith('-'):
            continue

        # Check if path begins with /
        if part.startswith('/'):
            return False, "absolute paths are not allowed"

        # Check if path equals ..
        if part == '..':
            return False, "upward directory traversal (..) is not allowed"

        # Check if path contains ../
        if '../' in part:
            return False, "upward directory traversal (../) is not allowed"

        # Check if path contains /..
        if '/..' in part:
            return False, "upward directory traversal (/..) is not allowed"

    return True, ""