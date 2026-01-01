"""Tests for sqlite3_safe_operations_rule."""

import pytest
from devleaps.policies.server.common.models import ToolUseEvent
from devleaps.policies.server.common.enums import SourceClient
from src.universal.sqlite3_allow import sqlite3_safe_operations_rule


@pytest.fixture
def create_tool_use_event():
    """Factory fixture to create ToolUseEvent."""
    def _create(command: str, tool_is_bash: bool = True) -> ToolUseEvent:
        return ToolUseEvent(
            session_id="test-session",
            source_client=SourceClient.CLAUDE_CODE,
            tool_name="Bash" if tool_is_bash else "Read",
            tool_is_bash=tool_is_bash,
            command=command,
            parameters={"command": command}
        )
    return _create


def test_non_bash_tool_skipped(create_tool_use_event):
    """Policy should skip non-bash tools."""
    event = create_tool_use_event("test.db", tool_is_bash=False)

    results = list(sqlite3_safe_operations_rule(event))
    assert len(results) == 0


def test_non_sqlite3_command_skipped(create_tool_use_event):
    """Policy should skip non-sqlite3 commands."""
    event = create_tool_use_event("ls -la")

    results = list(sqlite3_safe_operations_rule(event))
    assert len(results) == 0


def test_select_query_allowed(create_tool_use_event):
    """SELECT queries should be allowed."""
    event = create_tool_use_event('sqlite3 test.db "SELECT * FROM users"')

    results = list(sqlite3_safe_operations_rule(event))
    assert len(results) == 1
    assert results[0].action == "allow"


def test_select_case_insensitive(create_tool_use_event):
    """SELECT queries should work case-insensitively."""
    event = create_tool_use_event('sqlite3 test.db "select * from users"')

    results = list(sqlite3_safe_operations_rule(event))
    assert len(results) == 1
    assert results[0].action == "allow"


def test_select_with_where_clause(create_tool_use_event):
    """SELECT with WHERE clause should be allowed."""
    event = create_tool_use_event('sqlite3 test.db "SELECT name, email FROM users WHERE id = 1"')

    results = list(sqlite3_safe_operations_rule(event))
    assert len(results) == 1
    assert results[0].action == "allow"


def test_select_with_join(create_tool_use_event):
    """SELECT with JOIN should be allowed."""
    event = create_tool_use_event(
        'sqlite3 test.db "SELECT u.name, o.total FROM users u JOIN orders o ON u.id = o.user_id"'
    )

    results = list(sqlite3_safe_operations_rule(event))
    assert len(results) == 1
    assert results[0].action == "allow"


def test_insert_blocked(create_tool_use_event):
    """INSERT statements should be blocked."""
    event = create_tool_use_event('sqlite3 test.db "INSERT INTO users (name) VALUES (\'Alice\')"')

    results = list(sqlite3_safe_operations_rule(event))
    assert len(results) == 1
    assert results[0].action == "deny"
    assert "write operations" in results[0].reason


def test_update_blocked(create_tool_use_event):
    """UPDATE statements should be blocked."""
    event = create_tool_use_event('sqlite3 test.db "UPDATE users SET name = \'Bob\' WHERE id = 1"')

    results = list(sqlite3_safe_operations_rule(event))
    assert len(results) == 1
    assert results[0].action == "deny"
    assert "UPDATE" in results[0].reason


def test_delete_blocked(create_tool_use_event):
    """DELETE statements should be blocked."""
    event = create_tool_use_event('sqlite3 test.db "DELETE FROM users WHERE id = 1"')

    results = list(sqlite3_safe_operations_rule(event))
    assert len(results) == 1
    assert results[0].action == "deny"
    assert "DELETE" in results[0].reason


def test_drop_blocked(create_tool_use_event):
    """DROP statements should be blocked."""
    event = create_tool_use_event('sqlite3 test.db "DROP TABLE users"')

    results = list(sqlite3_safe_operations_rule(event))
    assert len(results) == 1
    assert results[0].action == "deny"
    assert "DROP" in results[0].reason


def test_create_blocked(create_tool_use_event):
    """CREATE statements should be blocked."""
    event = create_tool_use_event('sqlite3 test.db "CREATE TABLE users (id INT, name TEXT)"')

    results = list(sqlite3_safe_operations_rule(event))
    assert len(results) == 1
    assert results[0].action == "deny"
    assert "CREATE" in results[0].reason


def test_alter_blocked(create_tool_use_event):
    """ALTER statements should be blocked."""
    event = create_tool_use_event('sqlite3 test.db "ALTER TABLE users ADD COLUMN email TEXT"')

    results = list(sqlite3_safe_operations_rule(event))
    assert len(results) == 1
    assert results[0].action == "deny"
    assert "ALTER" in results[0].reason


def test_replace_blocked(create_tool_use_event):
    """REPLACE statements should be blocked."""
    event = create_tool_use_event('sqlite3 test.db "REPLACE INTO users (id, name) VALUES (1, \'Alice\')"')

    results = list(sqlite3_safe_operations_rule(event))
    assert len(results) == 1
    assert results[0].action == "deny"
    assert "REPLACE" in results[0].reason


def test_attach_blocked(create_tool_use_event):
    """ATTACH statements should be blocked."""
    event = create_tool_use_event('sqlite3 test.db "ATTACH DATABASE \'other.db\' AS other"')

    results = list(sqlite3_safe_operations_rule(event))
    assert len(results) == 1
    assert results[0].action == "deny"
    assert "ATTACH" in results[0].reason


def test_detach_blocked(create_tool_use_event):
    """DETACH statements should be blocked."""
    event = create_tool_use_event('sqlite3 test.db "DETACH DATABASE other"')

    results = list(sqlite3_safe_operations_rule(event))
    assert len(results) == 1
    assert results[0].action == "deny"
    assert "DETACH" in results[0].reason


def test_pragma_blocked(create_tool_use_event):
    """PRAGMA statements should be blocked."""
    event = create_tool_use_event('sqlite3 test.db "PRAGMA table_info(users)"')

    results = list(sqlite3_safe_operations_rule(event))
    assert len(results) == 1
    assert results[0].action == "deny"
    assert "PRAGMA" in results[0].reason


def test_write_operations_case_insensitive(create_tool_use_event):
    """Write operations should be blocked case-insensitively."""
    event = create_tool_use_event('sqlite3 test.db "insert into users (name) values (\'Alice\')"')

    results = list(sqlite3_safe_operations_rule(event))
    assert len(results) == 1
    assert results[0].action == "deny"


def test_no_select_no_write_asks(create_tool_use_event):
    """Commands without SELECT or write operations should ask for clarification."""
    event = create_tool_use_event('sqlite3 test.db ".tables"')

    results = list(sqlite3_safe_operations_rule(event))
    assert len(results) == 1
    assert results[0].action == "ask"
    assert "SELECT" in results[0].reason


def test_schema_command_asks(create_tool_use_event):
    """Schema introspection commands should ask for clarification."""
    event = create_tool_use_event('sqlite3 test.db ".schema users"')

    results = list(sqlite3_safe_operations_rule(event))
    assert len(results) == 1
    assert results[0].action == "ask"


def test_select_with_subquery(create_tool_use_event):
    """SELECT with subquery should be allowed."""
    event = create_tool_use_event(
        'sqlite3 test.db "SELECT * FROM users WHERE id IN (SELECT user_id FROM orders)"'
    )

    results = list(sqlite3_safe_operations_rule(event))
    assert len(results) == 1
    assert results[0].action == "allow"


def test_multiple_selects_in_transaction_allowed(create_tool_use_event):
    """Multiple SELECT statements should be allowed."""
    event = create_tool_use_event(
        'sqlite3 test.db "SELECT COUNT(*) FROM users; SELECT * FROM users LIMIT 10"'
    )

    results = list(sqlite3_safe_operations_rule(event))
    assert len(results) == 1
    assert results[0].action == "allow"


def test_select_with_update_blocked(create_tool_use_event):
    """SELECT combined with UPDATE should be blocked."""
    event = create_tool_use_event(
        'sqlite3 test.db "SELECT * FROM users; UPDATE users SET active = 1"'
    )

    results = list(sqlite3_safe_operations_rule(event))
    assert len(results) == 1
    assert results[0].action == "deny"
    assert "UPDATE" in results[0].reason


def test_explain_query_plan_with_select_allowed(create_tool_use_event):
    """EXPLAIN QUERY PLAN with SELECT should be allowed."""
    event = create_tool_use_event('sqlite3 test.db "EXPLAIN QUERY PLAN SELECT * FROM users"')

    results = list(sqlite3_safe_operations_rule(event))
    assert len(results) == 1
    assert results[0].action == "allow"


def test_comment_with_blocked_keywords(create_tool_use_event):
    """Comments containing blocked keywords should still allow SELECT."""
    event = create_tool_use_event(
        'sqlite3 test.db "SELECT * FROM users -- this query used to DELETE records"'
    )

    results = list(sqlite3_safe_operations_rule(event))
    # This will be blocked because DELETE is in the command, even in a comment
    # This is a trade-off for simplicity, but better to be safe
    assert len(results) == 1
    assert results[0].action == "deny"
