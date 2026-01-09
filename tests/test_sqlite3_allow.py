import pytest
from src.universal.sqlite3_allow import sqlite3_safe_operations_rule
from tests.helpers import assert_allow, assert_deny, assert_pass, assert_ask


def test_non_bash_tool_skipped(bash_event):
    assert_pass(sqlite3_safe_operations_rule, bash_event("test.db", tool_is_bash=False))


def test_non_sqlite3_command_skipped(bash_event):
    assert_pass(sqlite3_safe_operations_rule, bash_event("ls -la"))


def test_select_query_allowed(bash_event):
    assert_allow(sqlite3_safe_operations_rule, bash_event('sqlite3 test.db "SELECT * FROM users"'))


def test_select_case_insensitive(bash_event):
    assert_allow(sqlite3_safe_operations_rule, bash_event('sqlite3 test.db "select * from users"'))


def test_select_with_where_clause(bash_event):
    assert_allow(sqlite3_safe_operations_rule, bash_event('sqlite3 test.db "SELECT name, email FROM users WHERE id = 1"'))


def test_select_with_join(bash_event):
    assert_allow(sqlite3_safe_operations_rule, bash_event('sqlite3 test.db "SELECT u.name, o.total FROM users u JOIN orders o ON u.id = o.user_id"'))


def test_insert_blocked(bash_event):
    assert_deny(sqlite3_safe_operations_rule, bash_event('sqlite3 test.db "INSERT INTO users (name) VALUES (\'Alice\')"'), "write operations")


def test_update_blocked(bash_event):
    assert_deny(sqlite3_safe_operations_rule, bash_event('sqlite3 test.db "UPDATE users SET name = \'Bob\' WHERE id = 1"'), "UPDATE")


def test_delete_blocked(bash_event):
    assert_deny(sqlite3_safe_operations_rule, bash_event('sqlite3 test.db "DELETE FROM users WHERE id = 1"'), "DELETE")


def test_drop_blocked(bash_event):
    assert_deny(sqlite3_safe_operations_rule, bash_event('sqlite3 test.db "DROP TABLE users"'), "DROP")


def test_create_blocked(bash_event):
    assert_deny(sqlite3_safe_operations_rule, bash_event('sqlite3 test.db "CREATE TABLE users (id INT, name TEXT)"'), "CREATE")


def test_alter_blocked(bash_event):
    assert_deny(sqlite3_safe_operations_rule, bash_event('sqlite3 test.db "ALTER TABLE users ADD COLUMN email TEXT"'), "ALTER")


def test_replace_blocked(bash_event):
    assert_deny(sqlite3_safe_operations_rule, bash_event('sqlite3 test.db "REPLACE INTO users (id, name) VALUES (1, \'Alice\')"'), "REPLACE")


def test_attach_blocked(bash_event):
    assert_deny(sqlite3_safe_operations_rule, bash_event('sqlite3 test.db "ATTACH DATABASE \'other.db\' AS other"'), "ATTACH")


def test_detach_blocked(bash_event):
    assert_deny(sqlite3_safe_operations_rule, bash_event('sqlite3 test.db "DETACH DATABASE other"'), "DETACH")


def test_pragma_blocked(bash_event):
    assert_deny(sqlite3_safe_operations_rule, bash_event('sqlite3 test.db "PRAGMA table_info(users)"'), "PRAGMA")


def test_write_operations_case_insensitive(bash_event):
    assert_deny(sqlite3_safe_operations_rule, bash_event('sqlite3 test.db "insert into users (name) values (\'Alice\')"'))


def test_no_select_no_write_asks(bash_event):
    """Commands without SELECT or write operations should ask for clarification."""
    assert_ask(sqlite3_safe_operations_rule, bash_event('sqlite3 test.db ".tables"'), "SELECT")


def test_schema_command_asks(bash_event):
    assert_ask(sqlite3_safe_operations_rule, bash_event('sqlite3 test.db ".schema users"'))


def test_select_with_subquery(bash_event):
    assert_allow(sqlite3_safe_operations_rule, bash_event('sqlite3 test.db "SELECT * FROM users WHERE id IN (SELECT user_id FROM orders)"'))


def test_multiple_selects_in_transaction_allowed(bash_event):
    assert_allow(sqlite3_safe_operations_rule, bash_event('sqlite3 test.db "SELECT COUNT(*) FROM users; SELECT * FROM users LIMIT 10"'))


def test_select_with_update_blocked(bash_event):
    assert_deny(sqlite3_safe_operations_rule, bash_event('sqlite3 test.db "SELECT * FROM users; UPDATE users SET active = 1"'), "UPDATE")


def test_explain_query_plan_with_select_allowed(bash_event):
    assert_allow(sqlite3_safe_operations_rule, bash_event('sqlite3 test.db "EXPLAIN QUERY PLAN SELECT * FROM users"'))


def test_comment_with_blocked_keywords(bash_event):
    """Comments containing blocked keywords should still block (trade-off for simplicity)."""
    assert_deny(sqlite3_safe_operations_rule, bash_event('sqlite3 test.db "SELECT * FROM users -- this query used to DELETE records"'))
