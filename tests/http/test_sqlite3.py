"""
HTTP Integration Tests for SQLite3 Commands

Tests SQLite3 read-only policy: SELECT allowed, write operations denied.
Uses real Claude Code event payloads and TestClient.
"""

from tests.http.conftest import check_policy


# ============================================================================
# SELECT Queries - ALLOW
# ============================================================================

def test_sqlite3_select_simple(client, base_event):
    """Simple SELECT should be allowed"""
    check_policy(client, base_event, "sqlite3 db.sqlite 'SELECT * FROM users'", "allow")


def test_sqlite3_select_with_where(client, base_event):
    """SELECT with WHERE clause should be allowed"""
    check_policy(client, base_event, "sqlite3 db.sqlite 'SELECT * FROM users WHERE id = 1'", "allow")


def test_sqlite3_select_with_join(client, base_event):
    """SELECT with JOIN should be allowed"""
    check_policy(client, base_event, "sqlite3 db.sqlite 'SELECT * FROM users JOIN orders ON users.id = orders.user_id'", "allow")


def test_sqlite3_select_count(client, base_event):
    """SELECT COUNT should be allowed"""
    check_policy(client, base_event, "sqlite3 db.sqlite 'SELECT COUNT(*) FROM users'", "allow")


def test_sqlite3_select_lowercase(client, base_event):
    """SELECT in lowercase should be allowed"""
    check_policy(client, base_event, "sqlite3 db.sqlite 'select * from users'", "allow")


def test_sqlite3_select_multiline(client, base_event):
    """Multi-line SELECT should be allowed"""
    check_policy(client, base_event, "sqlite3 db.sqlite 'SELECT id, name FROM users LIMIT 10'", "allow")


def test_sqlite3_pragma_readonly(client, base_event):
    """PRAGMA read-only queries should be allowed"""
    check_policy(client, base_event, "sqlite3 db.sqlite 'PRAGMA table_info(users)'", "allow")


def test_sqlite3_explain_query(client, base_event):
    """EXPLAIN queries should be allowed"""
    check_policy(client, base_event, "sqlite3 db.sqlite 'EXPLAIN SELECT * FROM users'", "allow")


def test_sqlite3_dot_schema(client, base_event):
    """.schema command should be allowed"""
    check_policy(client, base_event, "sqlite3 db.sqlite '.schema'", "allow")


def test_sqlite3_dot_tables(client, base_event):
    """.tables command should be allowed"""
    check_policy(client, base_event, "sqlite3 db.sqlite '.tables'", "allow")


# ============================================================================
# Write Operations - DENY
# ============================================================================

def test_sqlite3_insert_denied(client, base_event):
    """INSERT should be denied"""
    data = check_policy(client, base_event, "sqlite3 db.sqlite 'INSERT INTO users VALUES (1, \"test\")'", "deny")
    reason = data["hookSpecificOutput"]["permissionDecisionReason"].lower()
    assert "read-only" in reason or "not allowed" in reason


def test_sqlite3_update_denied(client, base_event):
    """UPDATE should be denied"""
    check_policy(client, base_event, "sqlite3 db.sqlite 'UPDATE users SET name = \"new\" WHERE id = 1'", "deny")


def test_sqlite3_delete_denied(client, base_event):
    """DELETE should be denied"""
    check_policy(client, base_event, "sqlite3 db.sqlite 'DELETE FROM users WHERE id = 1'", "deny")


def test_sqlite3_drop_denied(client, base_event):
    """DROP TABLE should be denied"""
    check_policy(client, base_event, "sqlite3 db.sqlite 'DROP TABLE users'", "deny")


def test_sqlite3_create_denied(client, base_event):
    """CREATE TABLE should be denied"""
    check_policy(client, base_event, "sqlite3 db.sqlite 'CREATE TABLE test (id INT)'", "deny")


def test_sqlite3_alter_denied(client, base_event):
    """ALTER TABLE should be denied"""
    check_policy(client, base_event, "sqlite3 db.sqlite 'ALTER TABLE users ADD COLUMN age INT'", "deny")


def test_sqlite3_truncate_denied(client, base_event):
    """TRUNCATE should be denied"""
    check_policy(client, base_event, "sqlite3 db.sqlite 'TRUNCATE TABLE users'", "deny")


def test_sqlite3_begin_transaction_denied(client, base_event):
    """BEGIN TRANSACTION should be denied"""
    check_policy(client, base_event, "sqlite3 db.sqlite 'BEGIN TRANSACTION'", "deny")


def test_sqlite3_commit_denied(client, base_event):
    """COMMIT should be denied"""
    check_policy(client, base_event, "sqlite3 db.sqlite 'COMMIT'", "deny")


def test_sqlite3_rollback_denied(client, base_event):
    """ROLLBACK should be denied"""
    check_policy(client, base_event, "sqlite3 db.sqlite 'ROLLBACK'", "deny")


def test_sqlite3_attach_denied(client, base_event):
    """ATTACH DATABASE should be denied"""
    check_policy(client, base_event, "sqlite3 db.sqlite 'ATTACH DATABASE \"other.db\" AS other'", "deny")


def test_sqlite3_detach_denied(client, base_event):
    """DETACH DATABASE should be denied"""
    check_policy(client, base_event, "sqlite3 db.sqlite 'DETACH DATABASE other'", "deny")


def test_sqlite3_vacuum_denied(client, base_event):
    """VACUUM should be denied"""
    check_policy(client, base_event, "sqlite3 db.sqlite 'VACUUM'", "deny")


def test_sqlite3_reindex_denied(client, base_event):
    """REINDEX should be denied"""
    check_policy(client, base_event, "sqlite3 db.sqlite 'REINDEX'", "deny")


def test_sqlite3_analyze_denied(client, base_event):
    """ANALYZE should be denied"""
    check_policy(client, base_event, "sqlite3 db.sqlite 'ANALYZE'", "deny")


# ============================================================================
# Edge Cases
# ============================================================================

def test_sqlite3_with_flags(client, base_event):
    """sqlite3 with flags and SELECT should be allowed"""
    check_policy(client, base_event, "sqlite3 -header -column db.sqlite 'SELECT * FROM users'", "allow")


def test_sqlite3_no_query_ask(client, base_event):
    """sqlite3 without query should ask"""
    check_policy(client, base_event, "sqlite3 db.sqlite", "ask")
