"""
HTTP Integration Tests for small universal additions:
date, dig, md5, pgrep (allowed) and disown, node -e (denied).
"""

from tests.http.conftest import check_policy

# ============================================================================
# date - display only
# ============================================================================


def test_date_allowed(client, base_event):
    check_policy(client, base_event, "date", "allow")


def test_date_utc_allowed(client, base_event):
    check_policy(client, base_event, "date -u", "allow")


def test_date_format_allowed(client, base_event):
    check_policy(client, base_event, "date +%Y-%m-%d", "allow")


def test_date_utc_with_format_allowed(client, base_event):
    check_policy(client, base_event, "date -u +%Y-%m-%dT%H:%M:%SZ", "allow")


def test_date_quoted_format_with_spaces_allowed(client, base_event):
    check_policy(client, base_event, "date '+%Y-%m-%d %H:%M:%S'", "allow")
    check_policy(client, base_event, 'date -u "+%Y-%m-%d %H:%M"', "allow")


def test_date_adjusted_display_allowed(client, base_event):
    check_policy(client, base_event, "date -v-1d +%Y-%m-%d", "allow")


def test_date_set_operand_defers_to_user(client, base_event):
    """A bare operand sets the clock on macOS - no allow."""
    check_policy(client, base_event, "date 0101120026", None)


def test_date_gnu_set_defers_to_user(client, base_event):
    check_policy(client, base_event, "date -s '2026-01-01 12:00'", None)


# ============================================================================
# dig, md5, pgrep
# ============================================================================


def test_dig_allowed(client, base_event):
    check_policy(client, base_event, "dig +short example.com", "allow")


def test_md5_safe_path_allowed(client, base_event):
    check_policy(client, base_event, "md5 file.txt", "allow")


def test_md5_quiet_allowed(client, base_event):
    check_policy(client, base_event, "md5 -q file.txt", "allow")


def test_md5_unsafe_path_denied(client, base_event):
    check_policy(client, base_event, "md5 /etc/passwd", "deny")


def test_md5_parent_path_denied(client, base_event):
    check_policy(client, base_event, "md5 ../app-production.db.bak", "deny")


def test_md5_repeated_option_not_allowed(client, base_event):
    check_policy(client, base_event, "md5 -q /etc/passwd -q file.txt", "deny")


def test_pgrep_allowed_with_pkill_guidance(client, base_event):
    data = check_policy(client, base_event, "pgrep -f uvicorn", "allow")
    assert "pkill" in data["hookSpecificOutput"]["permissionDecisionReason"]


# ============================================================================
# disown, node -e - denied
# ============================================================================


def test_disown_denied_with_background_guidance(client, base_event):
    data = check_policy(client, base_event, "disown", "deny")
    assert "run_in_background" in data["hookSpecificOutput"]["permissionDecisionReason"]


def test_disown_with_job_denied(client, base_event):
    check_policy(client, base_event, "disown %1", "deny")


def test_node_eval_denied(client, base_event):
    check_policy(client, base_event, "node -e 'console.log(1)'", "deny")


def test_node_eval_long_denied(client, base_event):
    check_policy(client, base_event, "node --eval 'console.log(1)'", "deny")


def test_node_eval_equals_denied(client, base_event):
    check_policy(client, base_event, "node --eval='console.log(1)'", "deny")


def test_node_print_denied(client, base_event):
    check_policy(client, base_event, "node -p 'process.version'", "deny")


def test_node_print_eval_combined_denied(client, base_event):
    check_policy(client, base_event, "node -pe 'process.version'", "deny")


def test_node_script_defers_to_user(client, base_event):
    check_policy(client, base_event, "node scripts/build.js", None)
