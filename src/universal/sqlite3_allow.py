"""Allows sqlite3 SELECT queries but blocks write operations."""

import re
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def sqlite3_safe_operations_rule(input_data: ToolUseEvent):
    """Allow sqlite3 with SELECT queries, block write operations."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Match sqlite3 commands
    if not re.match(r'^sqlite3\s+', command):
        return

    # Convert to uppercase for case-insensitive matching
    command_upper = command.upper()

    # List of write operations to block
    write_operations = [
        'INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER',
        'CREATE', 'REPLACE', 'ATTACH', 'DETACH', 'PRAGMA'
    ]

    # Check for write operations
    has_write_operation = any(
        re.search(rf'\b{op}\b', command_upper) for op in write_operations
    )

    if has_write_operation:
        yield PolicyHelper.deny(
            "By policy, sqlite3 write operations (INSERT, UPDATE, DELETE, DROP, ALTER, "
            "CREATE, REPLACE, ATTACH, DETACH, PRAGMA) are not allowed.\n"
            "Only SELECT queries are permitted for database read operations."
        )
        return

    # Check if command contains SELECT
    has_select = re.search(r'\bSELECT\b', command_upper)

    if has_select:
        yield PolicyHelper.allow()
        return

    # If no SELECT and no write operations, ask for clarification
    yield PolicyHelper.ask(
        "This sqlite3 command doesn't appear to contain a SELECT query. "
        "Only SELECT queries are allowed by policy. "
        "If you need to perform a read operation, please use SELECT."
    )
